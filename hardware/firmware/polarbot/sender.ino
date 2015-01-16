#include <SoftwareSerial.h>

SoftwareSerial mySerial(GPIO1,GPIO2);
/*
minicom -D /dev/ttyUSB0  -b 9600
then CTRL-A Z E to enable local echo

http://www.instructables.com/id/Processing-Controls-RC-Car-with-XBee-modules/step10/XBee-Configuration/

Type +++ to enter command mode, CoolTerm will respond with OK
ATID 1
ATMY 1
ATDH 0 
ATDL 2 
ATBD 3
ATWR
*/


void setup_sender()  
{
//send
  mySerial.begin(9600);
}

void xbee_send(char val)                     // run over and over again
{
      mySerial.write(val);
}

void penDown()
{
    xbee_send(90);
}
void penUp()
{
    xbee_send(30);
}
