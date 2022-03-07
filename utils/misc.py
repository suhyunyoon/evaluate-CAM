import os
import copy
import yaml
import logging
from torch.utils.tensorboard import SummaryWriter

# deepcopy src values into target(Union(target, src) but src primary)
def inherit_dict(target, src):
    ret = copy.deepcopy(target)

    for k, v in src.items():
        # hierachical dictionary
        if isinstance(v, dict):
            ret[k] = inherit_dict(ret.get(k,dict()), v)

        # value(or list)
        else:
            ret[k] = copy.deepcopy(v)

    return ret

# Load Configuration yaml file (currently useless)
def load_config(cfg_path):

    with open(cfg_path) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    # Inherit base configuration
    if 'base' in cfg:
        cfg_parent = load_config(cfg['base'])
        cfg = inherit_dict(cfg_parent, cfg)
    
    return cfg


# Overwrite read config yaml file into args
def overwrite_args_from_yaml(args, cfg_path):
    if cfg_path == '':
        return
    with open(cfg_path, 'r', encoding='utf-8') as f:
        dic = yaml.load(f.read(), Loader=yaml.Loader)
        for k in dic:
            setattr(args, k, dic[k])
            

def make_log_dir(args):
    # Logging dir
    log_path = os.path.join(args.log_dir, args.log_name)
    if os.path.exists(log_path):
        # Overwrite existing dir
        if args.log_overwrite:
            import shutil
            shutil.rmtree(log_path)

        # Make another directory
        else:
            # cur_time = str(int(time.time()))
            # log_path += '_' + cur_time
            # args.log_name += '_' +str(int(time.time()))
            raise FileExistsError(f'{args.log_name} Already Exists!')
    # Make log directory
    os.mkdir(log_path)  

    return log_path


# add args.log_path
def make_logger(args):
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    
    if args.cls_skip:
        log_path = os.path.join(args.log_dir, args.log_name)
    else:
        log_path = make_log_dir(args)

    formatter = logging.Formatter(fmt="[%(asctime)s %(levelname)s] %(message)s")

    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename=os.path.join(log_path, 'main.log'))  

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    #sys.stdout = LoggerWriter(logger.warning)
    #sys.stderr = LoggerWriter(logger.error)
    
    return logger, log_path
    

# class LoggerWriter:
#     def __init__(self, level):
#         self.level = level

#     def write(self, message):
#         if message != '\n':
#             self.level(message)

#     def flush(self):
#         self.level(sys.stderr)

class TensorBoardLogger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.writer = SummaryWriter(os.path.join(self.log_dir, 'tensorboard'))

    def update(self, tb_dict, it, suffix=None):
        if suffix is None:
            suffix = ''
        for key, value in tb_dict.items():
            self.writer.add_scalar(suffix + key, value, it)