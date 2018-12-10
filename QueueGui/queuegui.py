#!/usr/bin/env python

import Tkinter as tk
import tkFileDialog
import subprocess as sub
import glob
from datetime import datetime, timedelta
import os
from collections import OrderedDict

class QueueGui(object):
    """Docstring"""

    buttonfont = ("Arial", 10)
    qfont = ("Arial", 8)

    def __init__(self, master):
        #master.geometry("1200x500")
        master.title("QueueGui")

        self.topframeleft = tk.Frame(master)
        self.topframeleft.grid(row=0, column=0, sticky="nsew")

        self.topframeright = tk.Frame(master)
        self.topframeright.grid(row=0, column=1, sticky="nsew")

        self.midframe = tk.Frame(master)
        self.midframe.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.midframe.grid_columnconfigure(0, weight=1)
        self.midframe.grid_rowconfigure(0, weight=1)

        self.botframe = tk.Frame(master)
        self.botframe.grid(row=2, column=0, sticky="nsew")

        self.status_options = OrderedDict()
        self.status_options["All Jobs"] = "all"
        self.status_options["Running Jobs"] = "r"
        self.status_options["Pending Jobs"] = "pd"
        self.status_options["Completed Jobs"] = "cd"
        self.status_options["Cancelled Jobs"] = "ca"
        self.status_options["Timeouted Jobs"] = "to"

        
        self.status = tk.StringVar()
        self.status.set(self.status_options.keys()[0]) # set default value to "All"

        self.user = tk.StringVar()
        self.user.set("ambr") # set default user to "ambr"

        self.job_starttime_options = [datetime.now().date() - timedelta(days=i) for i in range(14)]
        self.job_starttime = tk.StringVar()
        self.job_starttime.set(datetime.now().date()) # default option will be the current date

        self.place_widgets()

        self.get_q()

        self.log_update("Welcome to QueueGui!")


    def place_widgets(self):
        # top frame widgets

        b_refresh = tk.Button(self.topframeleft, text="Update Queue", command=self.get_q, font=self.buttonfont)
        b_refresh.grid(row=1, column=0, sticky="ew", pady=5, padx=5)

        b_openoutput = tk.Button(self.topframeleft, text="Output file", command=self.open_output, font=self.buttonfont)
        b_openoutput.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        b_openinput = tk.Button(self.topframeleft, text="Input File", command=self.open_input, font=self.buttonfont)
        b_openinput.grid(row=1, column=2, sticky="ew", pady=5, padx=5)

        b_showsubmitscript = tk.Button(self.topframeleft, text="Submit Script", command=self.open_submitscript, font=self.buttonfont)
        b_showsubmitscript.grid(row=2, column=0)

        optionmenu_jobhis_starttime = tk.OptionMenu(self.topframeleft, self.job_starttime, *self.job_starttime_options)
        optionmenu_jobhis_starttime.grid(row=2, column=3, sticky="ew")

        b_showjobinfo = tk.Button(self.topframeleft, text="Job Info", command=self.open_jobinfo, font=self.buttonfont)
        b_showjobinfo.grid(row=2, column=1)

        b_jobhis = tk.Button(self.topframeleft, text="Job History", command=self.open_jobhis, font=self.buttonfont)
        b_jobhis.grid(row=2, column=2)

        status_menu = tk.OptionMenu(self.topframeleft, self.status, *self.status_options.keys())
        status_menu.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        b_cpu = tk.Button(self.topframeleft, text="Check CPU Usage", command=self.cpu_usage, font=self.buttonfont)
        b_cpu.grid(row=0, column=2, sticky="ew", pady=5, padx=5)
        
        b_quepasa = tk.Button(self.topframeleft, text="Que Pasa?", command=self.quepasa, font=self.buttonfont)
        b_quepasa.grid(row=1, column=3, sticky="ew", pady=5, padx=5)
        
        b_moldenout = tk.Button(self.topframeleft, text="Molden Output", command=self.molden_output, font=self.buttonfont)
        b_moldenout.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
        
        self.entry_user = tk.Entry(self.topframeleft, width=10)
        self.entry_user.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        self.entry_user.insert(0, self.user.get()) 
        self.entry_user.bind("<Return>", self.get_q)
 

        yscroll_log = tk.Scrollbar(self.topframeright)
        yscroll_log.grid(row=0, rowspan=3, column=5, pady=2, padx=2, sticky="ns")
        self.log = tk.Text(self.topframeright, yscrollcommand=yscroll_log.set, bg="black", fg="white", height=7, width=90)
        self.log.grid(row=0, rowspan=3, column=4, pady=5, padx=5, sticky="nsew")
        yscroll_log.config(command=self.log.yview)

        # mid frame widgets
        yscrollbar = tk.Scrollbar(self.midframe)
        yscrollbar.grid(row=0, column=1, sticky="ns", pady=2, padx=2)

        self.txt = tk.Text(self.midframe, wrap=tk.NONE, yscrollcommand=yscrollbar.set, bg="black", fg="white")
        self.txt.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)
        self.txt.config(state=tk.DISABLED)
        self.txt.tag_configure("even_line", background="#13001a")
        self.txt.tag_configure("odd_line", background="#001a00")
        self.txt.tag_raise(tk.SEL)

        yscrollbar.config(command=self.txt.yview)

        # bottom frame widgets
        b_exit = tk.Button(self.botframe, text="Quit", bg="black", fg="red", command=master.destroy, font=self.buttonfont)
        b_exit.grid(row=0, column=0, pady=5, padx=5)

        b_killjob = tk.Button(self.botframe, text="Kill Selected Job", bg="black", fg="red", command=self.kill_job, font=self.buttonfont)
        b_killjob.grid(row=0, column=1, pady=5, padx=5)

        b_convertme = tk.Button(self.botframe, text="Launch ConvertMe", bg="blue", fg="white", command=self.launch_convertme, font=self.buttonfont)
        b_convertme.grid(row=0, column=2, pady=5, padx=5)

    def get_q(self, *args): # *args needed for binding the function to <Return> entry user field
        
        self.user.set(self.entry_user.get())
        self.status.set(self.status_options[self.status.get()])

        if self.user.get().strip() == "" or self.user.get() == "all":
            cmd = ["squeue", "-S", "i", "-o", "%.18i %.9P %.40j %.8u %.8T %.10M %.9l %.6D %R"]
        else:
            cmd = ["squeue", "-u", self.user.get(), "-t", self.status.get() , "-S", "i", "-o", "%.18i %.9P %.40j %.8u %.8T %.10M %.9l %.6D %R"]

        process = sub.Popen(cmd, stdout=sub.PIPE)

        q = process.stdout.readlines()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for i, job in enumerate(q):
            if i % 2 == 0:
                self.txt.insert(tk.END, job, "even_line")
            else:
                self.txt.insert(tk.END, job, "odd_line")

        self.txt.config(state=tk.DISABLED)

        # now make sure the current status shown in the drop down menu corresponds to the same status used for the last job history command
        for stat, opt in self.status_options.items():
            if self.status.get() == opt:
                self.status.set(stat)
                break

    def cpu_usage(self):
        cmd = ["squeue", "-o", "%u %C %t"]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        q = process.stdout.read().splitlines()
        
        # Total number of CPU on Stallo, taken from
        # https://www.sigma2.no/content/stallo
        cpu_stallo_total = float(14116)
        
        # all jobs in queue
        q = map(lambda x: x.split(), q)
        # only running jobs
        r = filter(lambda x: x[-1] == "R", q)
        # only pending jobs
        p = filter(lambda x: x[-1] == "PD", q)
        
        # Initialize list to contain the users from all jobs
        users = []
        for job in q:
            for j,el in enumerate(job):
                if j == 0:
                    users.append(el)
        
        # Initialize a dict in which the sum of all CPUs will be accumulated
        cpu_running = {usr: 0 for usr in set(users)}
        cpu_pending = {usr: 0 for usr in set(users)}
        
        # perform the sum for running cpus
        for job in r:
            for u in cpu_running.keys():
                if u in job:
                    cpu_running[u] += int(job[1])
        # and for pending cpus. Getting users from same list as above, to keep the order consistent
        for job in p:
            for u in cpu_running.keys():
                if u in job:
                    cpu_pending[u] += int(job[1])
        
        
        # zipping and sorting
        zipped = sorted(zip(cpu_running.keys(), [c for user, c in cpu_running.items()], [c for user, c in cpu_pending.items()]), key=lambda x: x[1], reverse=True)
        
        # unzipping
        user, cpu_running, cpu_pending = zip(*zipped)
        # get ratio of running cpus to stallo's total
        oftotal = map(lambda x: str(float(x) / cpu_stallo_total * 100)[0:5], cpu_running)
        
        # adding arrow to username.. First convert from tuple to list
        user = [u for u in user]
        choco = ["ambr", "mobst", "ljilja", "diego", "kathrin"]
        for i,u in enumerate(user):
            if u in choco:
                user[i] += " <<<<<<"
        
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        self.txt.insert(tk.END, "User    Run     %     Pending\n")
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        

        maxlen = (max(len(x) for x in user) , max(len(str(x)) for x in cpu_running), max(len(str(x)) for x in oftotal), max(len(str(x)) for x in cpu_pending))
        for i in range(len(user)):
                self.txt.insert(tk.END, "{} {} {} {} {} {} {}\n".format(user[i], 
                                                                 (maxlen[0] - len(user[i])) * " ",
                                                                 cpu_running[i],
                                                                 (maxlen[1] - len(str(cpu_running[i]))) * " ",
                                                                 oftotal[i],
                                                                 (maxlen[2] - len(oftotal[i])) * " ",
                                                                 cpu_pending[i]))
                
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        
        # convert back to floats for the summation
        oftotal = map(float, oftotal)
        self.txt.insert(tk.END, "SUM: {} {} {} {} {} {}\n".format((maxlen[0] - 4) * " ",
                                                                  sum(cpu_running),
                                                                  (maxlen[1] - len(str(sum(cpu_running)))) * " ",
                                                                  sum(oftotal),
                                                                  (maxlen[2] - len(str(sum(oftotal)))) * " ",
                                                                  sum(cpu_pending)))
        self.txt.insert(tk.END, "-----------------------------------------------------------------\n")
        self.txt.config(state=tk.DISABLED)

    def open_output(self):
        outputfile = self.eval_workfile("output")
        if "ErrorCode_" in outputfile:
            self.log_update(outputfile)
            return outputfile

        f = open(outputfile, "r")
        lines = f.readlines()
        f.close()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def open_input(self):
        inputfile = self.eval_workfile("input")
        if "ErrorCode_" in inputfile:
            self.log_update(inputfile)
            return inputfile

        f = open(inputfile, "r")
        lines = f.readlines()
        f.close()

        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in lines:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def quepasa(self):
        outputfile = self.eval_workfile("output")
        if "ErrorCode_" in outputfile:
            self.log_update(outputfile)
            return outputfile

        self.log_update("Que Pasa? {}".format(outputfile))
        sub.call(["bash", "/home/ambr/bin/gaussian_howsitgoing.sh", "{}".format(outputfile)])

    def molden_output(self):
        outputfile = self.eval_workfile("output")
        if "ErrorCode_" in outputfile:
            self.log_update(outputfile)
            return outputfile

        self.log_update("molden {}".format(outputfile))
        sub.call(["molden", "{}".format(outputfile)])

    def select_text(self):
        if self.txt.tag_ranges(tk.SEL):
            return self.txt.get(tk.SEL_FIRST, tk.SEL_LAST)
        else:
            self.log_update("No PID selected. ErrorCode_las02")
            return "ErrorCode_las02"

    def eval_workfile(self,filetype):
        pid = self.select_text()
        try: # check that the selected text is a valid pid
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_xal49")
            return "ErrorCode_xal49"

        # define the workdir. using user variable to access other users files
        workdir = "/global/work/{}/{}/".format(self.user.get(), pid)
        # getting jobname from the scontrol command
        jobname = self.get_jobname(pid)

        # determine which extension to use
        if filetype == "output":
            ext = [".out"]
        elif filetype == "input":
            ext = [".com", ".inp"]
        else:
            self.log_update("Filetype '{}' not supported. ErrorCode_tot91".format(filetype))
            return "ErrorCode_tot91"

        usefile = None
        for x in ext:
            f = workdir + jobname + x
            if os.path.isfile(f):
                usefile = f
                break # a useable file was found, so we break out of the loop. no need to evaluate other extensions

        # make sure some file actually was found by checking that the initial value of 'usefile' did not change from None
        if usefile == None:
            self.log_update("No file found. ErrorCode_tyr86")
            return "ErrorCode_tyr86"

        # now we attempt to open the found file
        try:
            s = open(usefile, "r")
            s.close()
            self.log_update("Using this file: {}".format(usefile))
            return usefile # return the fill path to the file, to be used by subsequent methods
        except IOError:
            self.log_update("File not found: {}. ErrorCode_poz32".format(usefile))
            return "ErrorCode_poz32"

    def get_jobname(self, pid):
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_mel73")
            return "ErrorCode_mel73"

        cmd = ["scontrol", "show", "jobid", pid]

        process = sub.Popen(cmd, stdout=sub.PIPE)
        return process.stdout.read().splitlines()[0].split()[1].split("=")[1]
        
    
    def kill_job(self):
        pid = self.select_text()
        cmd = ["scancel", pid]
        self.log_update(" ".join(cmd))
        sub.call(cmd)
        self.get_q()

    def clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log_update("Welcome to QueueGui!")
        return None

    def log_update(self, msg):
        logmsg = "[{}] {}\n".format(str(datetime.now().time()).split(".")[0], msg)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, logmsg)
        self.log.config(state=tk.DISABLED)
        self.log.see("end")
        return None

    def open_submitscript(self):
        pid = self.select_text()
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_toj60")
            return ErrorCode_toj60

        cmd = ["scontrol", "show", "jobid", "-dd", pid]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        subscript = process.stdout.read().split("BatchScript=\n")[1]
       
        self.log_update(" ".join(cmd))
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in subscript:
            self.txt.insert(tk.END, line)
        self.txt.config(state=tk.DISABLED)

    def open_jobinfo(self):
        pid = self.select_text()
        try:
            int(pid)
        except ValueError:
            self.log_update("PID must be an integer. ErrorCode_toj66")
            return ErrorCode_toj66

        cmd = ["scontrol", "show", "jobid", pid]
        process = sub.Popen(cmd, stdout=sub.PIPE)
        jobinfo = process.stdout.read().split()

        self.log_update(" ".join(cmd))
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)
        for line in jobinfo:
            self.txt.insert(tk.END, line + "\n")
        self.txt.config(state=tk.DISABLED)

    def open_jobhis(self):
        self.user.set(self.entry_user.get())
        self.status.set(self.status_options[self.status.get()])

        if self.user.get().strip() == "":
            self.log_update("No user selected. ErrorCode_hus28")
            return "ErrorCode_hus28"

        if self.status.get() == self.status_options["All Jobs"]:
            cmd = ["sacct", "-u", self.user.get(), "--starttime", self.job_starttime.get(), "--format=User,JobID,Jobname%50,state%20,time,nnodes%2,CPUTime,elapsed,Start"]
        else:
            cmd = ["sacct", "-u", self.user.get(), "-s", self.status.get(), "--starttime", self.job_starttime.get(), "--format=User,JobID,Jobname%50,state%20,time,nnodes%2,CPUTime,elapsed,Start"]

        process = sub.Popen(cmd, stdout=sub.PIPE)
        jh = process.stdout.readlines()

        # now get rid of useless lines in the history
        history = [jh[0]] # start with the header present in the list
        for line in jh:
            try:
                int(line.split()[1])
            except ValueError:
                continue
            history.append(line)
       
        self.log_update("Showing job history for {} starting from {}".format(self.user.get(), self.job_starttime.get()))
      
        self.txt.config(state=tk.NORMAL)
        self.txt.delete(1.0, tk.END)

        for i, line in enumerate(history):
            if i % 2 == 0:
                self.txt.insert(tk.END, line, "even_line")
            else:
                self.txt.insert(tk.END, line, "odd_line")
        
        self.txt.config(state=tk.DISABLED)

        # now make sure the current status shown in the drop down menu corresponds to the same status used for the last job history command
        for stat, opt in self.status_options.items():
            if self.status.get() == opt:
                self.status.set(stat)
                break

    def launch_convertme(self):
        sub.call(["python", "/home/ambr/bin/convertme.py"])

##########################################################
# run program
if __name__ == "__main__":
    master = tk.Tk()
    app = QueueGui(master)
    master.mainloop()
