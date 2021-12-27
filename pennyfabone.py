import math
import smtplib

PUSH_PRODUCTION = 'push'
PULL_PRODUCTION = 'pull'

class Station():
    def __init__(self, ct):
        '''
          * ct: The cycle time of the station 
        '''
        self.wip = 0
        self.working = 0
        self.cycle_time = ct
        self.output = 0

    def add_wip(self, i):
        self.wip += i

    def work(self):
        if self.wip >= 1/self.cycle_time:
            self.working += 1/self.cycle_time
        if self.working >= 1:
            self.output = math.floor(self.working)
            self.working -= self.output
            self.wip -= self.output

    def out(self):
        output = self.output
        self.output = 0
        return output

class SingleFlowFourStations:
    def __init__(self, cts=[2, 2, 6, 2], hours=40, threshold=10, target=100, mode=PUSH_PRODUCTION, start=0):
        '''
        * cts: The Cycle Time of stations
        * hours: The working hours
        * threshold: The limit for WIP
        * target: The target yield for production
        * mode: The production model, PUSH_PRODUCTION or PULL_PRODUCTION
        * start: The starting time for "PULL" production
        '''
        self.stations = []
        for ct in cts:
            self.stations.append(Station(ct))

        self.hours = hours
        self.threshold = threshold
        self.target = target
        self.mode = mode
        self.start = start

        self.finish = 0
        self.time_tick = 0
        self.lead_time = 0
        if(mode == PULL_PRODUCTION):
            self.load_time = []
            for i in range(start, self.hours):
                if (i - start) % max(station.cycle_time for station in self.stations) == 0:
                    self.load_time.append(i)
                if len(self.load_time) == target:
                    break

    def run_all(self):
        print('Threshold:', self.threshold)
        while self.time_tick <= self.hours:
            if self.total_wip() >= self.threshold:
                self.exception_message("Total wip %d have met the limit %d"%(self.total_wip(), self.threshold))
            if(self.mode == PUSH_PRODUCTION):
                if self.stations[0].wip == 0 and self.total_wip() < self.threshold:
                    self.stations[0].add_wip(1)
            elif(self.mode == PULL_PRODUCTION):
                if self.stations[0].wip == 0 and self.time_tick in self.load_time and self.total_wip() < self.threshold:
                    self.stations[0].add_wip(1)
            self.work_step()
            self.work_flow()
            self.dump_wip()
            if (self.finish == self.target and self.lead_time == 0):
                self.lead_time = self.time_tick
            self.time_tick += 1
        return self.finish, self.lead_time

    def work_step(self):
        for station in self.stations:
            station.work()

    def work_flow(self):
        out = 0
        for station in self.stations:
            station.add_wip(out)
            out = station.out()
        self.finish += out

    def dump_wip(self):
        print(":%d:" % (self.time_tick), end=" ")
        for index, station in enumerate(self.stations):
            print("s%d:%d, " % (index, station.wip), end="")
        print("finish:%d, total wip:%d" % (self.finish, self.total_wip()))

    def total_wip(self):
        return sum(s.wip for s in self.stations)

    def exception_message(self,exception_msg):
        smtp = smtplib.SMTP('smtp.gmail.com',587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('pennyfabone@gmail.com','pswd4penny')
        from_addr='pennyfabone@gmail.com'
        to_addr='judyfang0108@gmail.com'
        msg="Subject:Penny Fab One Exception\n"\
            +exception_msg
        status=smtp.sendmail(from_addr, to_addr, msg)
        if status=={}:
            print("Exception sent")