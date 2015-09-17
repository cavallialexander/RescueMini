/*
 
A thin shim translating Dynamixel commands from Serial 2 to Dynamixel.
Very much a work-in-progress. For example, we can't read from the servos yet.
 
Note that all values in <> are ASCII decimal integers.
<pos> is a value from 0 to 1023.
<vel> is a velocity, 0 to 1023 is forward, 1024-2047 is negative.
 
Possible commands:
 
"Wj<ID>" to make motor <ID> enter joint mode.
"Wp<ID>,<pos>,<vel>" to make motor <ID> move to position <pos> with velocity <vel>.
"Ww<ID>,<add>,<val>" to write <val> to register <add> of motor <ID>.
 
*/
 
Dynamixel Dxl(1);
#define PRESENT_POS_L 0x36
#define PRESENT_POS_H 0x37
 
void setup()
{
  Serial2.begin(57600);
  Dxl.begin(3);
}
 
byte blockingRead()
{
  while (!Serial2.available()) delay(10);
  return Serial2.read();
}
 
void processWrite(byte cmd, byte id)
{
          switch (cmd)
        {
          case 'j':
            Dxl.jointMode(id);
            break;
          case 'p':
            int pos, vel;
            if (!(readInt(&pos) && readInt(&vel))) break;
            Dxl.setPosition(id, pos, vel);
            break;
          case 'w':
            int add, val;
            if (!(readInt(&add) && readInt(&val))) break;
            Dxl.writeWord(id, add, val);
            break;
        }
}
 
void loop()
{
  while (Serial2.available())
  {
    // Wait for a start byte, "W" for write or "R" for read.
    byte inByte = blockingRead();
    switch (inByte)
    {
      case 'W':
      {
        byte cmd = blockingRead();
        byte id = blockingRead();
        processWrite(cmd, id);
      }
        break;
      case 'R':
        byte ID = blockingRead();
        readFromDynamixel(ID);
        break;
    }    
 
  }
}
 
boolean readInt(int * outVal)
{
  byte inBuffer[sizeof(short)];
  int i;
  for (i = 0; i < sizeof(short); i ++)
  {
    inBuffer[i] = blockingRead();
  }
  *outVal = *((short*)inBuffer);
  return true;
}
 
void readFromDynamixel(byte id)
{
  unsigned int pos = Dxl.readWord(id, PRESENT_POS_H) << 8 | Dxl.readWord(id, PRESENT_POS_L);
  Serial2.write(id);
  Serial2.write(pos);
  Serial2.print(id);
  Serial2.print(" ");
  Serial2.print(pos);
}