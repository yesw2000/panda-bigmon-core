
#import cx_Oracle
import pandas as pd
import matplotlib.dates as md
from matplotlib import pyplot as plt
import os
from django.db import connection
from core.common.models import JediTasks
import StringIO


class TaskProgressPlot:

    def __init__(self):
        pass

    def get_task_start(self,taskid):
        query={}
        query['jeditaskid'] = taskid
        starttime = JediTasks.objects.filter(**query).values('starttime')
        if len(starttime) > 0:
            return starttime[0]
        else:
            return None


    def prepare_task_profile(self,frame):
        if len(frame) > 0:
            firstrow = [(frame.STARTTIME[0], frame.STARTTIME[0], 0), ]
            return pd.DataFrame.from_records(firstrow, columns=frame.columns).append(frame, ignore_index=True)
        else:
            return frame


    def get_raw_task_profile(self,taskid):
        cur = connection.cursor()
        cur.execute("select starttime, endtime, row_number() over (PARTITION BY jeditaskid order by endtime ) as njobs from ATLAS_PANDAARCH.JOBSARCHIVED WHERE JEDITASKID={0} and JOBSTATUS='finished'" .format(taskid))
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=['starttime','endtime','njobs'])


    def get_raw_task_profile_fresh(self,taskid):
        cur = connection.cursor()
        cur.execute("select starttime, creationtime, endtime, row_number() over (PARTITION BY jeditaskid order by endtime ) as njobs FROM ("
                    "SELECT DISTINCT starttime, creationtime, endtime, pandaid, jeditaskid FROM JOBSARCHIVED WHERE JEDITASKID={0} and JOBSTATUS='finished' UNION ALL "
                    "SELECT DISTINCT starttime, creationtime, endtime, pandaid, jeditaskid FROM JOBSARCHIVED4 WHERE JEDITASKID={0} and JOBSTATUS='finished')t1".format(taskid))
        rows = cur.fetchall()

        if len(rows) > 0:
            data = {'starttime': [row[0] for row in rows],
                    'creationtime': [row[1] for row in rows],
                    'endtime': [row[2] for row in rows],
                    'njobs': [row[3] for row in rows]}
            return pd.DataFrame(data, columns=['starttime','creationtime','endtime', 'njobs'])
        else:
            None


    def make_profile_graph(self,frame, taskid):
        fig = plt.figure(figsize=(20, 15))
        plt.title('Execution profile for task {0}, NJOBS={1}'.format(taskid, len(frame) - 1), fontsize=24)
        plt.xlabel("Job completion time", fontsize=18)
        plt.ylabel("Number of completed jobs", fontsize=18)
        plt.plot(frame.ENDTIME, frame.NJOBS, '.r')
        return fig


    def make_verbose_profile_graph(self,frame, taskid, status=None, daterange=None):
        plt.style.use('fivethirtyeight')
        fig = plt.figure(figsize=(20, 15))
        plt.locator_params(axis='x', nbins=30)
        plt.locator_params(axis='y', nbins=30)
        if status is not None:
            plt.title('Execution profile for task {0}, NJOBS={1}, STATUS={2}'.format(taskid, len(frame), status),
                      fontsize=24)
        else:
            plt.title('Execution profile for task {0}, NJOBS={1}'.format(taskid, len(frame)), fontsize=24)
        plt.xlabel("Job completion time", fontsize=18)
        plt.ylabel("Number of completed jobs", fontsize=18)
        plt.axvline(x=self.get_task_start(taskid)['starttime'], color='b', linewidth=4, label="Task start time")
        plt.xticks(rotation=25)
        ax = plt.gca()
        xfmt = md.DateFormatter('%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        #plt.xlim(daterange)
        plt.plot(frame.endtime, frame.njobs, '.r', label='Job ENDTIME')
        plt.plot(frame.starttime, frame.njobs, '.g', label='Job STARTTIME')
        plt.plot(frame.creationtime, frame.njobs, '.b', label='Job CREATIONTIME')
        plt.legend(loc='lower right')
        return fig


    def save_task_profile(self,taskid):
        frame = self.get_raw_task_profile(taskid)
        fig = self.make_profile_graph(frame, taskid)
        plt.savefig(os.path.join("task_profiles", str(taskid) + ".png"))
        plt.close(fig)


    def show_task_profile(self,taskid):
        frame = self.get_raw_task_profile(taskid)
        fig = self.make_profile_graph(frame, taskid)
        plt.show()
        plt.close(fig)


    def get_task_status(self,taskid):
        query={}
        query['jeditaskid'] = taskid
        status = JediTasks.objects.filter(**query).values('status')
        if len(status) > 0:
            return status[0]
        else:
            return None


    def show_verbose_task_profile(self,taskid, daterange=None):
        frame = self.get_raw_task_profile_fresh(taskid)
        fig = self.make_verbose_profile_graph(frame, taskid, self.get_task_status(taskid), daterange)
        plt.show()
        plt.close(fig)


    def get_task_profile(self,taskid):
        frame = self.get_raw_task_profile_fresh(taskid)
        if frame is not None:
            fig = self.make_verbose_profile_graph(frame, taskid, self.get_task_status(taskid))
            imgdata = StringIO.StringIO()
            fig.savefig(imgdata, format='png')
            imgdata.seek(0)
            return imgdata.buf
        return None