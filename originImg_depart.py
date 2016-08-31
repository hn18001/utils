import os,sys
import myutils as mu
import os,shutil

def depart(dirname):
        imglist = mu.getImageListRecursive(dirname)
        for abspath in imglist:
                filename = os.path.basename(abspath)
                filecount = int(filename.split('.')[0])
                print "filecount: ",filecount
                if filecount % 2 != 0:
                        shutil.copy(abspath, origin_path + filename)


if __name__ == "__main__":
        dirname = '/home/lizhichao/data/Subtitle/News_Caption/'
        origin_path = '/home/lizhichao/data/Subtitle/Origin_Img/'
        depart(dirname)
