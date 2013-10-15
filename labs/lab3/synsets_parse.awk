#!/bin/awk -f
{
	c=split($1,a," ")
}
{
	d=split($2,b,"; ")
}
{
	for (x=1; x<=c; x++){
		for(y=1; y<=d; y++){
			print(a[x] ", " b[y]);
			}
	}
}
