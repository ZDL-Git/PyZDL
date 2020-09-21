import os
import subprocess
from os.path import exists

import cv2

from zdl.utils.env.installer import Installer
from zdl.utils.io.log import logger


class OpenposeInstaller(Installer):
    GIT_REPO_URL = 'https://github.com/CMU-Perceptual-Computing-Lab/openpose.git'
    COCO_MODEL_URL = 'https://media.githubusercontent.com/media/foss-for-synopsys-dwc-arc-processors/synopsys-caffe-models/master/caffe_models/openpose/caffe_model/pose_iter_440000.caffemodel'
    COCO_MODEL_URL2 = 'http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/coco/pose_iter_440000.caffemodel'
    OPENPOSE_PATH = '/content/openpose/'
    OPENPOSE_RPATH = 'openpose'
    OPENPOSE_GREEN_PATH = '/content/openpose-green/'
    OPENPOSE_GREEN_RPATH = 'openpose-green'
    GPU_PACKAGE = 'openpose-Ubuntu_18_04-Tesla_P100.tar.gz'
    GPU_PACKAGE_K80 = 'openpose-Ubuntu_18_04-Tesla_K80.tar.gz'
    CPU_PACKAGE = 'openpose-Ubuntu_18_04-CPU.tar.gz'

    DRIVE_PACKAGE_PATH = '/content/DriveNotebooks/package/'
    LOCAL_PACKAGE_PATH = '/content/package/'
    CMAKE_CMD = 'cmake -D BUILD_PYTHON=ON -D CMAKE_BUILD_TYPE=Release ..'
    CMAKE_DEBUG_CMD = 'cmake -D BUILD_PYTHON=ON ..'
    CMAKE_CPU_CMD = 'cmake -D BUILD_PYTHON=ON -D GPU_MODE=CPU_ONLY -D USE_MKL=Off -D CMAKE_BUILD_TYPE=Release ..'
    CMAKE_CPU_DEBUG_CMD = 'cmake -D BUILD_PYTHON=ON -D GPU_MODE=CPU_ONLY -D USE_MKL=Off ..'

    @classmethod
    def _prepare(cls):
        # assert os.path.exists(cls.DRIVE_PACKAGE_PATH)
        os.makedirs(cls.LOCAL_PACKAGE_PATH, exist_ok=True)

        # see: https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/949
        # install new CMake because of CUDA10
        logger.info('installing dependency cmake...')
        cmake_package = 'cmake-3.13.0-Linux-x86_64.tar.gz'
        install_cmake = f'cd {cls.LOCAL_PACKAGE_PATH} ' \
                        f'&& ls {cmake_package} ' \
                        f'|| wget -q https://cmake.org/files/v3.13/{cmake_package} ' \
                        f'&& tar xfz {cmake_package} --strip-components=1 -C /usr/local'
        install_dependencies = f'apt-get -qq install -y libatlas-base-dev libprotobuf-dev libleveldb-dev ' \
                               f'libsnappy-dev libhdf5-serial-dev protobuf-compiler libgflags-dev libgoogle-glog-dev ' \
                               f'liblmdb-dev opencl-headers ocl-icd-opencl-dev libviennacl-dev'
        cls.checkCall(install_cmake)
        cls.checkCall(install_dependencies)

    @classmethod
    def onlineInstall(cls, mode='GPU'):
        if not exists(cls.OPENPOSE_PATH):
            cls._prepare()

            clone_openpose = f'git clone -q --depth 1 {cls.GIT_REPO_URL}'
            cls.checkCall(clone_openpose)

            # build openpose
            cmake_c = cls.CMAKE_DEBUG_CMD if mode == 'GPU' else cls.CMAKE_CPU_DEBUG_CMD
            compile = f'cd {cls.OPENPOSE_PATH} && rm - rf build || true && mkdir build && cd build && {cmake_c} && make - j `nproc` && make install'
            cls.checkCall(compile)
        else:
            logger.warning(f'[{cls.OPENPOSE_PATH}] already exists!')

    @classmethod
    def _getModeEnv(cls, mode, debug=True):
        if mode == 'GPU':
            _, gpu_info = subprocess.getstatusoutput('nvidia-smi --query-gpu=gpu_name --format=csv')
            if gpu_info.find('failed') >= 0:
                raise Exception('No GPU found!!!')
            elif 'P100' in gpu_info or 'P4' in gpu_info:
                logger.debug('P100')
                source_file = cls.GPU_PACKAGE
            elif 'K80' in gpu_info or 'T4' in gpu_info:
                logger.debug('K80')
                source_file = cls.GPU_PACKAGE_K80
            else:
                assert False, 'GPU card not compile!'

            cmake_c = cls.CMAKE_DEBUG_CMD if debug else cls.CMAKE_CMD
        else:
            source_file = cls.CPU_PACKAGE
            cmake_c = cls.CMAKE_CPU_DEBUG_CMD if debug else cls.CMAKE_CPU_CMD
        return cmake_c, source_file

    @classmethod
    def buildGreenVersion(cls, mode='GPU'):
        assert not os.path.exists(cls.OPENPOSE_GREEN_PATH), 'already exists!'
        cls._prepare()

        clone_openpose = f'git clone -q --depth 1 https://github.com/CMU-Perceptual-Computing-Lab/openpose.git {cls.OPENPOSE_GREEN_RPATH}'
        cls.checkCall(clone_openpose)
        cmake_c, tar_file_name = cls._getModeEnv(mode)
        build = f'cd {cls.OPENPOSE_GREEN_PATH} && rm -rf build || true && mkdir build ' \
                f'&& cd build && {cmake_c} && make -j`nproc` ' \
                f'&& cd /content && tar -czf {tar_file_name} {cls.OPENPOSE_GREEN_RPATH}'
        cls.checkCall(build)
        logger.info('finished.')

    @classmethod
    def rebuild(cls, build_path, mode='GPU', debug=True, clear=False, install=True, tar=False):
        cmake_c, tar_file_name = cls._getModeEnv(mode, debug)
        command = f'cd {build_path}'
        if clear:
            command += f'&& make clean && [[ "$PWD" =~ build ]] && rm -rf *'

        command += f'&& {cmake_c} && make -j`nproc`'

        if install:
            command += f'&& make install'
        if tar:
            command += f'&& tar -czf /content/{tar_file_name} {os.path.join(build_path, "..")}'
        cls.checkCall(command)

    @classmethod
    def installGreenVersion(cls, mode='GPU'):
        if exists(cls.OPENPOSE_GREEN_PATH):
            # if input("File exists, delete and republish? [y/n]:") == 'y':
            #     !rm -rf $OPENPOSE_GREEN_PATH
            # else:
            #     return
            logger.info(f'{cls.OPENPOSE_GREEN_PATH} already exists.')
            return

        cls._prepare()

        _, source_file = cls._getModeEnv(mode)

        logger.info(f'copy file...{source_file}')
        copy_pre_compiled_file = f'cp -rp {cls.DRIVE_PACKAGE_PATH}/{source_file} {cls.LOCAL_PACKAGE_PATH}/'
        cls.checkCall(copy_pre_compiled_file)

        logger.info('untar openpose...')
        decompression = f'tar xfz {cls.LOCAL_PACKAGE_PATH}/{source_file} --one-top-level={cls.OPENPOSE_GREEN_RPATH} --strip-components 1'
        cls.checkCall(decompression)

        logger.info('deploy openpose...')
        make_install = f'cd {cls.OPENPOSE_GREEN_PATH}/build/ && make install'
        cls.checkCall(make_install)

    @classmethod
    def install(cls):
        raise Exception('please use onlineInstall or installGreenVersion!')

    @classmethod
    def test(cls, imagepath_or_obj, params={}):
        if isinstance(imagepath_or_obj, str):
            img = cv2.imread(imagepath_or_obj)
        else:
            img = imagepath_or_obj

        import sys
        sys.path.append('/usr/local/python')
        # sys.path.append('/usr/local/lib')
        from openpose import pyopenpose as opp

        model_path = (cls.OPENPOSE_GREEN_PATH if os.path.exists(
            cls.OPENPOSE_GREEN_PATH) else cls.OPENPOSE_PATH) + '/models/'
        logger.info(f'using model path: {model_path}')
        full_params = {
            'model_folder': model_path,
            'model_pose': 'BODY_25',
            'number_people_max': 3,
            # 'net_resolution': '-1x368', # it is default value
            'logging_level': 3,
            'display': 0,
            'alpha_pose': 0.79,
            # 'face': 1,
            # 'hand': 1,
        }
        full_params.update(params)

        opWrapper = opp.WrapperPython()
        opWrapper.configure(full_params)
        opWrapper.start()
        datum = opp.Datum()
        datum.cvInputData = img
        opWrapper.emplaceAndPop([datum])
        logger.debug(datum.poseKeypoints)
        return datum

    @classmethod
    def downloadCocoModel(cls, dst_path):
        down = f'wget {cls.COCO_MODEL_URL} -P {dst_path}'
        cls.checkCall(down)
