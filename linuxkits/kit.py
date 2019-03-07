import subprocess
import os
import os.path

class LinuxKit(object):
    """
    """
    @staticmethod
    def edit_path_env(profile="/etc/profile",value="/usr/local/mysql/bin",action="insert"):
        env_py = os.path.join(os.path.dirname(__file__),'environment.py')
        cmd = "sudo python3 {0} --profile={1} --value={2} --action={3}".format(env_py,profile,value,action)
        subprocess.run(cmd,shell=True,capture_output=True)

    @staticmethod
    def get_disk_free_size(floder_path):
        """返回目录(分区)的空闲空间字节(B)
        """
        if os.path.isdir(floder_path):
            s = os.statvfs(floder_path)
            return s.f_bavail * s.f_bsize
        
        return None

    @staticmethod
    def get_file_size(file_path):
        """返回文件的大小字节(B)
        """
        if os.path.isfile(file_path):
            return os.path.getsize(file_path)

        return None


