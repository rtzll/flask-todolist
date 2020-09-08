if [ "\`wget http://localhost:8000/
 -O /dev/null -S --quiet 2>&1 | grep '200 OK'\`" != "" ];
then
   echo Test passed!

fi;
                                                                                         
