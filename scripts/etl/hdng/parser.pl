#!/usr/bin/perl

open(file, "variables.csv");
@data = <file>;
close(file);

foreach $item (@data)
{
   $item=~s/\r|\n//g;
   $item=~s/^\S//g;
   $item=~s/\"//g;
   my ($code, $name) = split(/\,/, $item);
   $code = uc $code;
#   print "$code\n";
   $names{$code} = $name;
}

while (<>)
{
   $id++;
   $str=$_;
   $str=~s/\r|\n//g;

   my @items = split(/\,/, $str);
   if ($id == 1)
   {
	@fields1 = @items;
   }
   elsif ($id == 2)
   {
	@fields2 = @items;
   }
   else
   {
	my ($cbsnr, $naam, $acode) = ($items[0], $items[1], $items[$#items]);
	$naam=~s/\"//g;
	#print "$cbsnr $naam\n";
	for ($i = 2; $i <= $#items; $i++)
 	{
	    $items[$i]=~s/\"//g;
	    my $year = $fields1[$i];
	    my $code = $fields2[$i];
	    $code=~s/\"//g;
	    $code=~s/^(\S)\d{3}/$1/g;
	    $ucode = $code;
	    $ucode=~s/^\S//g;
	    #print "$year $items[$i]\n";
	    if ($year && $names{$ucode} && $items[$i]) # && $acode)
	    {
		$names{$ucode}=~s/\"//g;
	        print "$cbsnr, $naam, $year, $code, $names{$ucode}, $items[$i], $acode\n";
	    }
	}
   }
}
