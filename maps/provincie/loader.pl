#!/usr/bin/perl

use LWP::Simple;
$url = "http://www.gemeentegeschiedenis.nl";
$page = get($url);

while ($page=~s/href\=\"(http\S+?\/provincie\/.+?)\">//)
{
   $url = $1;
   $url=~s/(provincie)\//$1\/json\//g;
   print "$url\n";
}
