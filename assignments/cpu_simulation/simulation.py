#!/usr/bin/python3 

from components.Event import Event
from components.Scheduler import Scheduler
import queue


input_file = "input_data/jobs_in_c.txt"

# load the file
f = open(input_file, "rt")
lines = f.readlines()
f.close()

events = queue.PriorityQueue()  # to process events in order
eventMap = {}                   # to have direct access to events

# put the events in a priority queue to keep them sorted
for line in lines:
    parts = line.split()
    time = int(parts[1].strip())
    if time not in eventMap:
        eventMap[time] = []
    if parts[0] == 'A':
        pid = int(parts[1].strip())
    else:
        pid = None
    eventMap[time].append(Event(parts, pid))

for time in eventMap:
    events.put(time) #, eventMap[time])

# main loop:
prevtime = 0

scheduler = Scheduler(eventMap, events)

dispatcher = {'A': scheduler.arrival,
              'D': scheduler.display,
              'T': scheduler.terminate,
              'I': scheduler.io,
              'C': scheduler.io_complete,
              'E': scheduler.expired,
              'S': scheduler.signal,
              'W': scheduler.wait
              }

while not events.empty():
    nextEventTime = events.get()
    nextEvents = eventMap[nextEventTime]
    scheduler.currentTime = nextEventTime

    if scheduler.cpu.running != None:
        if scheduler.cpu.running.pid == 40:
            i=0
        transcurred = scheduler.currentTime - scheduler.cpu.running.last_event 
        scheduler.cpu.running.last_event = scheduler.currentTime
        scheduler.cpu.running.quantum -= transcurred
        scheduler.cpu.running.time_left -= transcurred

    # sort the events
    if len(nextEvents) > 1:
        nextEvents.sort()

    for event in nextEvents:  
        if event.arrival == 7459:
           i=0
        print("Event: %s   Time: %d"%(event.kind, event.arrival))
        dispatcher[event.kind](event)

    prevtime = nextEventTime

scheduler.display_final_stats()

