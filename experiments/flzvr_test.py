from tetheredvr.proxy import JSONStimulusOSGController
from tetheredvr.observers import SimulatedObserver, CarModelSocketObserver
import sys
import math
import time
import random


def distance(pos0, pos1):
    dx = pos0['x'] - pos1['x']
    dy = pos0['y'] - pos1['y']
    dz = pos0['z'] - pos1['z']
    return math.sqrt(dx**2 + dy**2 + dz**2)


class MyCustomExperiment(object):

    def __init__(self, osg_file, csv_output=sys.stdout):
        # the proxy instance allows us to talk to the display server
        self.ds_proxy = JSONStimulusOSGController()
        # create the observer
        self.observer = CarModelSocketObserver(self._observer_callback)
        # load the provided OSG file
        self.ds_proxy.set_stimulus_plugin('StimulusOSG')
        self.ds_proxy.load_osg(osg_file)
        # default state
        self.experiment_setup()

    def _observer_callback(self, info_dict):
        print info_dict
        self.move_fixed_observer(**info_dict)

    def move_fixed_observer(self, **kwargs):
        x = -kwargs.get('x')
        y = -kwargs.get('y')
        z = -kwargs.get('z')

        p0_x, p0_y = self.post0_position['x'], self.post0_position['y']
        p1_x, p1_y = self.post1_position['x'], self.post1_position['y']
        p2_x, p2_y = self.post2_position['x'], self.post2_position['y']

        self.ds_proxy.move_node('post0', x + p0_x, y + p0_y, 0)
        self.ds_proxy.move_node('post1', x + p1_x, y + p1_y, 0)
        self.ds_proxy.move_node('post2', x + p2_x, y + p2_y, 0)

    def experiment_start(self):
        # self.recorder.start()
        self.observer.start_observer()
        self.experiment_conditions_main_loop()

    def experiment_stop(self):
        # self.observer.stop()
        # self.recorder.stop()
        pass

    def randomize_post_positions(self):
        circle_idxs = set()
        while len(circle_idxs) < 3:
            circle_idxs.add(random.randint(0, 29))

        phi = math.pi * 2 / 30.0
        R = 0.3
        idxs = list(circle_idxs)

        self.post0_position['x'] = R * math.cos(phi * idxs[0])
        self.post0_position['y'] = R * math.sin(phi * idxs[0])
        self.post1_position['x'] = R * math.cos(phi * idxs[1])
        self.post1_position['y'] = R * math.sin(phi * idxs[1])
        self.post2_position['x'] = R * math.cos(phi * idxs[2])
        self.post2_position['y'] = R * math.sin(phi * idxs[2])

    def experiment_setup(self):
        """implement your custom experiment setup here"""
        # set initial observer position
        self.start_position = {'x': 0.0, 'y': 0.0, 'z': -0.07}
        self.ds_proxy.set_position(**self.start_position)

        self.post0_position = {'x': 0.0, 'y': 0.0, 'z': 0}
        self.post1_position = {'x': 0.0, 'y': 0.0, 'z': 0}
        self.post2_position = {'x': 0.0, 'y': 0.0, 'z': 0}

        self.randomize_post_positions()

        self.counter = {'post0': 0, 'post1': 0, 'post2': 0, 'outofbounds': 0}

    def experiment_logic(self):
        pass

    def experiment_conditions_main_loop(self):
        """implement your custom conditions here"""
        t0 = time.time() 
        with open('output-%f.csv' % time.time(), 'w') as output:
            while True:
                t = time.time() - t0
                pos = self.observer.position
                if distance(pos, self.post0_position) < 0.1:
                    # reached post 0
                    self.counter['post0'] += 1
                    self.observer.reset_to(**self.start_position)
                    self.randomize_post_positions()

                elif distance(pos, self.post1_position) < 0.1:
                    # reached post 0
                    self.counter['post1'] += 1
                    self.observer.reset_to(**self.start_position)
                    self.randomize_post_positions()

                elif distance(pos, self.post2_position) < 0.1:
                    # reached post 0
                    self.counter['post2'] += 1
                    self.observer.reset_to(**self.start_position)
                    self.randomize_post_positions()

                elif distance(pos, self.start_position) > 0.5:
                    self.counter['outofbounds'] += 1
                    self.observer.reset_to(**self.start_position)
                    self.randomize_post_positions()

                time.sleep(0.005)
                #print "XYZ(%3.2f, %3.2f, %3.2f)" % (pos['x'], pos['y'], pos['z']), self.counter             
                output.write('%.8f, %.8f, %.8f, %s\n' % (pos['x'], pos['y'], t, str(self.counter)))


if __name__ == "__main__":

    # OSGT files need to be in /home/flyvr/flyvr/FreemooVR/data
    ex = MyCustomExperiment(osg_file='three_posts_couzin.osgt')

    try:
        ex.experiment_start()

    except KeyboardInterrupt:
        sys.stderr.write('[QUIT] via user request <ctrl+c>')

    finally:
        ex.experiment_stop()
