import paramiko
import os

class ScriptRunner(object):

  def __init__(self, host):
    self.host = host

  def connect(self, username=None, password=None, key_filename=None):
    self.client = paramiko.SSHClient()
    self.client.set_missing_host_key_policy(
          paramiko.AutoAddPolicy())
    self.client.connect(self.host, username=username,
                        password=password, key_filename=key_filename)
    self.ftp = self.client.open_sftp()

  def run(self, command):
    stdin, stdout, stderr = self.client.exec_command(command)
    stdin.close()
    return stdout.channel.recv_exit_status(), stdout.read(), stderr.read()

  def run_file(self, file_path, daemonize=False):
    filename = os.path.basename(file_path)
    self.ftp.put(file_path, filename)
    command = "sudo sh %s" % filename
    if daemonize:
        command = "nohup " + command + ">& /dev/null < /dev/null &"
    stdin, stdout, stderr = self.client.exec_command(command)
    self.ftp.remove(filename)
    return stdout.channel.recv_exit_status(), stdout.read(), stderr.read()

  def close(self):
    self.ftp.close()
    self.client.close()
