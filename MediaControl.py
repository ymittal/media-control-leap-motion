###########################################################################
# This project was made during a Leap Motion hackathon sponsored by ACM   #
# (Bucknell University Chapter) and KEEN (Kern Entrepreneurship Education #
# Network) at Bucknell University on October 31, 2015.                    # 
###########################################################################

import Leap, sys, thread, time, math
from Leap import CircleGesture, SwipeGesture
from time import sleep

from pykeyboard import PyKeyboard
from AppKit import NSSystemDefined
from time import sleep

stop = False

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Let's our program run even when command line does not have focus
    controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']


    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        global listener
        
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        # Key Board instance 
        k = PyKeyboard()

        # Close Spotify when two fingers (almost) interest at right angles
        if (len(frame.hands) == 2):
            mostForwardOnHand1 = frame.hands[0].fingers.frontmost
            mostForwardOnHand2 = frame.hands[1].fingers.frontmost
            
            v1 = mostForwardOnHand1.direction   # directional vector - finger 1
            v2 = mostForwardOnHand2.direction   # directional vector - finger 2

            dot_product = v1.x*v2.x +v1.y*v2.y + v1.z*v2.z
            if abs(dot_product) < 0.1 and (v1.x == v2.x and v1.y == v2.y): # wiggle room of 0.1 for dot product
                k.press_key("command")
                k.tap_key("q")
                k.release_key("command")
                sleep(1000)

        # Get hands
        for hand in frame.hands:

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction
            
            # Get the hand's grab strength (fist or not)
            strength = hand.grab_strength # Fist closed if strength >= 0.6

            # Get the hand's 
            pitch = hand.direction.pitch
            roll = hand.palm_normal.roll 

            # Play Pause
            if strength >= 0.6 and stop == False:   # Fist -> Stop the music
                k.tap_key("space")
                global stop 
                stop = True 
            elif strength <= 0.6 and stop == True:
                # k.tap_key("space")
                global stop
                stop = False

            count = 0   # counts CircleGesture(s)
            
            # Get gestures                                                                                                                                                                                  
            for gesture in frame.gestures():
                # Swipe Gesture -> Skip media
                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    direction = swipe.direction.x
                    if direction < 0:
                        direc = 0   # Go back
                    else:
                        direc = 1   # Go forward
                        
                    if gesture.state == Leap.Gesture.STATE_STOP:    # Only run after gesture has ended
                        if direc == 0: 
                            k.tap_key("KEYTYPE_REWIND")
                            k.tap_key("KEYTYPE_REWIND")
                            sleep(2)    # sleep for 2 second
                        else:
                            k.tap_key("KEYTYPE_FAST")
                            sleep(2)    # sleep for 2 second  

                # Circle Gesture -> Change volume
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)

                    # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                        clockwiseness = "clockwise"
                    else:
                        clockwiseness = "counterclockwise"

                    if gesture.state == Leap.Gesture.STATE_STOP:
                        count += 1

            count = int(count)
            for i in range(0, count):      #revolutions
                sleep(0.05 )
                if clockwiseness == "clockwise":
                    print "clockwise"
                    k.tap_key('KEYTYPE_SOUND_UP') 
                else:
                    print "counter clockwise"
                    k.tap_key('KEYTYPE_SOUND_DOWN')
        return 0

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"


if __name__ == "__main__":
    main()