#!/bin/awk -f

BEGIN { 
	RS = "\-" ; FS = "\|"
}
{
	gsub(/\n/,"",$2);
	gsub(/\n/,"",$3);
	gsub(/\n/,"",$4);
	gsub(/\n/,"",$5);
	y=split($1,z,"\n");
	e=split($2,a,", ");
	f=split($3,b,", ");
	g=split($4,c,", ");
	h=split($5,d,", ");
}
{
           for (x=1; x<=e; x++){
           		if(a[x] ~ /[0-9]+/){
					print(z[2]","a[x]",1")
				}
			}
			for (x=1; x<=f; x++){
				if(b[x] ~ /[0-9]+/){
					print(z[2]","b[x]",2")
				}
			}
			for (x=1; x<=g; x++){
				if(c[x] ~ /[0-9]+/){
					print(z[2]","c[x]",3")
				}	
			}
			for (x=1; x<=h; x++){
				if(d[x] ~ /[0-9]+/){
					print(z[2]","d[x]",4")
				}
			}

}