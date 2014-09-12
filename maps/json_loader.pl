#!/usr/bin/perl

$path = "json";
mkdir $path unless (-d $json);
for ($i=1000; $i<=2014; $i++)
{
    load($i);
}

# simple test
#load(2014);
sub load
{
   my ($year, $DEBUG) = @_;
   my $filename = "$path/$year.json";

   $command = "wget http://api.gemeentegeschiedenis.nl/municipality/$year.geo.json -O $filename";
   $run = `$command`;
   $filesz = -s "$filename";
   unlink $filename if ($filesz eq 42); 
   return;
}
