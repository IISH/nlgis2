#!/usr/bin/perl

use LWP::Simple;
$url = "http://www.gemeentegeschiedenis.nl";
$page = get($url);

while ($page=~s/href\=\"(http\S+?\/provincie\/)(.+?)\">//)
{
   my ($url, $prov) = ($1, $2);
   $url = $url.$prov;
   $url=~s/(provincie)\//$1\/json\//g;
   push(@prov, $prov);
   #print "$url\n";
}
foreach $provname (@prov)
{
    print "\"$provname\", ";
}
