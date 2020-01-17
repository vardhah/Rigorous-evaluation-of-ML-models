import random
import numpy as np 

class xmlgen:

 track=["forza", "e-track-1" ,"e-track-2", "e-track-3","e-track-4","e-track-6","g-track-1", "g-track-2","g-track-3","corkscrew" ]
 track_len=[5784, 3243, 5380,4208,7041,4441, 2057, 3185,2483,3608]

 def __init__(self):
    self.selected_track=int()
    self.start_point=int()

 def x_state(self,num_track): 
  
  self.selected_track=int(np.random.randint(num_track,size=1))
  print("Track name:",self.track[self.selected_track])
  print("Track length:",self.track_len[self.selected_track])

  self.start_point= int(np.random.randint(int(self.track_len[self.selected_track])+1,size=1))
  print("Starting Point:",self.start_point)

  schema1="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE params SYSTEM "params.dtd">


    <params name="Quick Race">
    <section name="Header">
    <attstr name="name" val="Quick Race"/>
    <attstr name="description" val="Quick Race"/>
    <attnum name="priority" val="10"/>
    <attstr name="menu image" val="data/img/splash-qr.png"/>
    </section>

  <section name="Tracks">
    <attnum name="maximum number" val="1"/>
    <section name="1">
      <attstr name="name" val="""




  schema2="""/>
      <attstr name="category" val="road"/>
    </section>

  </section>

  <section name="Races">
    <section name="1">
      <attstr name="name" val="Quick Race"/>
    </section>

  </section>

  <section name="Quick Race">
    <attnum name="distance" unit="km" val="0"/>
    <attstr name="type" val="race"/>
    <attstr name="starting order" val="drivers list"/>
    <attstr name="restart" val="yes"/>
    <attnum name="laps" val="500"/>
    <section name="Starting Grid">
      <attnum name="rows" val="2"/>
      <attnum name="distance to start" val="""


  schema3="""/>
      <attnum name="distance between columns" val="20"/>
      <attnum name="offset within a column" val="10"/>
      <attnum name="initial speed" val="0"/>
      <attnum name="initial height" val="0.2"/>
    </section>

  </section>

  <section name="Drivers">
    <attnum name="maximum number" val="40"/>
    <attnum name="focused idx" val="0"/>
    <attstr name="focused module" val="scr_server"/>
    <section name="1">
      <attnum name="idx" val="0"/>
      <attstr name="module" val="scr_server"/>
    </section>

  </section>

  <section name="Configuration">
    <attnum name="current configuration" val="4"/>
    <section name="1">
      <attstr name="type" val="track select"/>
    </section>

    <section name="2">
      <attstr name="type" val="drivers select"/>
    </section>

    <section name="3">
      <attstr name="type" val="race config"/>
      <attstr name="race" val="Quick Race"/>
      <section name="Options">
        <section name="1">
          <attstr name="type" val="race length"/>
        </section>

      </section>

    </section>

  </section>

  <section name="Drivers Start List">
    <section name="1">
      <attstr name="module" val="olethros"/>
      <attnum name="idx" val="0"/>
    </section>

  </section>

</params>"""
  totalschema=[schema1, self.track[self.selected_track], schema2, str(self.start_point), schema3]
  x='"'.join(totalschema)
#print(x)

  with open('/home/torcsi/.torcs/config/raceman/quickrace.xml','w') as filehandle:
   filehandle.write(x)
  return [self.selected_track, self.start_point]
