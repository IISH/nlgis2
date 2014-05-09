#!/usr/bin/perl

opendir(DIR, $ARGV[0]);
@files = readdir(DIR);
closedir(DIR);

foreach $file (@files)
{
   if ($file=~/\.xls/)
   {
	print "$file\n";
#        $exe = `xls2csv -f -x xls/$file -c csv/$file.csv`;
	$db = `./parser.pl csv/$file.csv > db/$file.csv`;
   }
}
