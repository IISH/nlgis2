#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../libs";

use DB_File;
use DBI;
$| = 1;

my %dbconfig = loadconfig("/etc/apache2/nlgiss2.config");
$site = $dbconfig{root};
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{customdbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
my $dbh = DBI->connect("dbi:Pg:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});
use open ':std', ':encoding(utf-8)';

my $sqlstructure = "cbsnr, naam, year, code, indicator, value, amsterdam_code";
my @stritems = split(/\,\s*/, $sqlstructure);
$id = 0;
foreach $item (@stritems)
{
   $structure{$item} = $id; 
   $id++;
}

$lineID = 0;
%code2name = amsterdamcodes2names();
$data = enrich_dataset($ARGV[0]);
@items = split(/\n/sxi, $data);
foreach $str (@items)
{
    # Prevention from sql injection
    $sqlinjection = 0;
    $sqlinjection++ if ($str=~/(drop.+all|drop.+table)/sxi);
    $sqlinjection++ if ($str=~/(alter|create).+table/sxi);
    $sqlinjection++ if ($str=~/^select/sxi);
    exit(0) if ($sqlinjection);
    if ($str!~/^\".+?\"/)
    {
       $str = transform($str);
    }
    $str=~s/\r|\n//g;
    $str.=",";
    my $itemID = 0;
    my %thisdata;
    while ($str=~s/^\"(.*?)\"\,//)
    {
	my $item = $1;
	unless ($lineID)
	{
	    $names{$itemID} = $item;
	}
	else
	{
	    $data{$lineID}{$names{$itemID}} = $item;
	    $thisdata{$lineID}{$names{$itemID}} = $item;
	}
	$itemID++;
    }

    unless ($lineID)
    {
	%rnames = reverse %names;
	foreach $name (%rnames)
	{
	   $name=~s/\"//g;
	}
    }
    else
    {
        unless ($rnames{'value'})
        {
	    $values{$thisdata{$lineID}{'year'}}{$thisdata{$lineID}{'amsterdam_code'}}++;
        }
	else
	{
	    $values{$thisdata{$lineID}{'year'}}{$thisdata{$lineID}{'amsterdam_code'}} = $thisdata{$lineID}{'value'};
	    if ($thisdata{$lineID}{'value'} == 'NA')
	    {
		$values{$thisdata{$lineID}{'year'}}{$thisdata{$lineID}{'amsterdam_code'}} = 0;
	    }
	}
	if (!$rnames{'locations'} && !$rnames{'naam'} && !$rnames{'city'})
	{
	    my $amscode = $thisdata{$lineID}{'amsterdam_code'};
	    $data{$lineID}{'naam'} = $code2names{$amscode};
	}

	$topics{$thisdata{$lineID}{'code'}} = $thisdata{$lineID}{'indicator'};
    }
    $lineID++;
}

# Aggregation
foreach $lineID (sort keys %data)
{
   %items = %{$data{$lineID}};
   my ($code, $year) = ($items{'amsterdam_code'}, $items{'year'});
   unless ($items{'naam'})
   {
	$xcode=$code;
	$xcode=~s/\s+//g;
	$items{'naam'} = $code2name{$xcode}; 
   }
   print "I C$code $year $values{$year}{$code} $items{'naam'}\n" if ($DEBUG);
   foreach $name (sort keys %names)
   {
	print "$names{$name};;$items{$name}\n" if ($DEBUG);
   }

   unless ($added{$year}{$code})
   {
      $sql = "insert into datasets.data ($sqlstructure) values (";
      $items{'value'} = $values{$year}{$code} || '0';
      foreach $item (@stritems)
      {
	 $var = $items{$item} || '0';
	 $var=~s/^\s+|\s+$//g;
	 $dbhitem = $dbh->quote($var);
	 $sql.="$dbhitem,"
	 #print "$item $items{$item}\n";
      }

      $sql=~s/\,$//g;
      $sql.=");";
      #print "$sql\n";
      $dbh->do($sql);
   }

   $added{$year}{$code}++;
   # $sql = "insert into datasets.data (cbsnr, naam, year, code, indicator, value, amsterdam_code) values ('$cbsnr', $naamq, '$year', '$mcode', $indicator, '$items[$i]', '$acode');";
   #parser($str);
}

foreach $topic (sort %topics)
{
    if ($topics{$topic})
    {
       $name = $dbh->quote("$topics{$topic}");
       $insert = "insert into datasets.topics (topic_name, topic_code, datatype, topic_root, description, topic_name_rus) values ($name, '$topic', '0', '0', ' ', ' ')";
       $dbh->do($insert);
       #print "$insert\n";
    }
}

sub loadconfig
{
    my ($configfile, $DEBUG) = @_;
    my %config;

    open(conf, $configfile);
    while (<conf>)
    {
        my $str = $_;
        $str=~s/\r|\n//g;
        my ($name, $value) = split(/\s*\=\s*/, $str);
        $config{$name} = $value;
    }
    close(conf);

    return %config;
}

sub transform
{
   my ($str, $DEBUG) = @_;
   $str=~s/\r|\n//g;
   my @items = split(/\,/, $str);
   my $line;
   foreach $item (@items)
   {
      $line.="\"$item\",";
   }
   $line=~s/\,$//g;

   return $line;
}

sub enrich_dataset
{
   my ($filename, $DEBUG) = @_;
   my ($fulldataset, $extend, $extendheader, $majorcode, $majorind);

   # Get filename as code and indicator name
   if ($filename=~/^\S+\/(\S+)\.\w+/)
   {
       $majorcode = $1;
       $majorind = $1;
       $majorcode=~s/\W+//g;
       $majorcode=~s/\_//g;
       if ($majorcode=~/^(\S{5})/)
       {
           $majorcode = $1;
           if ($majorind=~/(\d+)/)
           {
              $majorcode.=$1;
           }
       }
   }

   open(file, $filename);
   @dataset = <file>;
   close(file);

   $data = "@dataset";
   $data=~s/\r/\n/g;
   my @items = split(/\n/, $data);
   foreach $str (@items)
   {
       $str=~s/\s*\,$//g;
       $str=~s/\;/\,/g;
   }
   $header = shift @items;
   unless ($header=~/\,code/i)
   {
        $extendheader = "code,indicator,";
        $extend = "$majorcode,$majorind,";
   }
   $mainheader = "$extendheader$header";
   $mainheader=~s/\"//g;
   $fulldataset = "$mainheader\n";
   foreach $str (@items)
   {
       $id++;
       $fulldataset.="$extend$str\n";
   }

   return $fulldataset;
}

sub loadlocations
{
    my ($dbh, $DEBUG) = @_;
    my %locations;
    $sqlquery = "select distinct(naam), amsterdam_code from datasets.data where naam<>'0'";
    my $sth = $dbh->prepare("$sqlquery");
    $sth->execute();

    while (my ($locname, $locid) = $sth->fetchrow_array())
    {
	$locations{$locid} = $locname;
    };

    return %locations;
}

sub amsterdamcodes2names
{
    my %amscodes;
    $url = "http://laborconflicts.socialhistory.org/api/lonlat";
    $wget = "/usr/bin/wget";
    $wget = "/usr/local/bin/wget" if (-e "/usr/local/bin/wget");

    # Find vocabulary first
    $vocfile = "$Bin/amsterdam.txt";
    if (-e $vocfile)
    {
        open(voc, $vocfile);
        @info = <voc>;
        close(voc);
        foreach $item (@info)
        {
            $item=~s/\r|\n//g;
            if ($item=~/^(\d+)\s+(.+)$/)
            {
                $amscodes{$1} = $2;
            }
        }
    }

    # Download latest lon-lat database if there is no vocabulary
    unless (keys %amscodes)
    {
        $lonlat = `$wget -q $url -O -`;
        my @loc = split(/\}\,/sxi, $lonlat);

        foreach $item (@loc)
        {
           $item=~s/\n/ /g;
           my %info;
           while ($item=~s/\s*\"(.+?)\":\s*\"(.+?)\"\,//)
           {
                $info{$1} = $2;
           }
           my ($amscode, $locname) = ($info{'amsterdam_code'}, $info{'municipality'});
           if ($amscode && !$exist{$amscode})
           {
                $amscodes{$amscode} = $locname;
                $exist{$amscode}++;
           };
        };

        open(voc, ">$vocfile");
        foreach $amscode (sort keys %amscodes)
        {
            print voc "$amscode $amscodes{$amscode}\n";
        }
        close(voc);
    }

    return %amscodes;
};
