from tensorflow import keras
from tensorflow.keras import backend as K
import tensorflow as tf
import pickle



class ModelCheckpoint(keras.callbacks.Callback):
    def __init__(self, file_path):
        super(ModelCheckpoint, self).__init__()
        self.file_path = file_path
        self.flag = True

    def on_epoch_end(self, epoch, logs=None):
        logs['lr'] = keras.backend.get_value(self.model.optimizer.lr)
        print(logs)
        if self.flag:
            self.checkpoint = tf.train.Checkpoint(base_model=self.model.base_model, fc=self.model.fc)
            self.flag = False

        logs.update({'epoch': epoch+1})
        self.checkpoint.save(self.file_path.format(**logs))

class IPC(keras.callbacks.Callback):
    def __init__(self, sock):
        super(IPC, self).__init__()
        self.sock = sock

    def on_train_batch_end(self, batch, logs=None):
        try:
            data = self.sock.recv(1024)
            if data == b'stop':
                self.model.stop_training = True
        except:
            pass

    def on_epoch_end(self, epoch, logs=None):
        logs.update({'epoch':epoch+1})
        logs['lr'] = keras.backend.get_value(self.model.optimizer.lr)
        print(logs)
        bytes = pickle.dumps(logs)
        self.sock.send(bytes)
    
# class LossHistory(keras.callbacks.Callback):
#     def __init__(self, log_dir):
#         import datetime
#         curr_time = datetime.datetime.now()
#         time_str = datetime.datetime.strftime(curr_time,'%Y_%m_%d_%H_%M_%S')
#         self.log_dir    = log_dir
#         self.time_str   = time_str
#         self.save_path  = os.path.join(self.log_dir, "loss_" + str(self.time_str))  
#         self.losses     = []
#         self.val_loss   = []
        
#         os.makedirs(self.save_path)

#     def on_epoch_end(self, epoch, logs={}):
#         self.losses.append(logs.get('loss'))
#         self.val_loss.append(logs.get('val_loss'))
#         with open(os.path.join(self.save_path, "epoch_loss_" + str(self.time_str) + ".txt"), 'a') as f:
#             f.write('epoch : ' + str(epoch + 1) + '\n')
#             f.write('loss : ' + str(logs.get('loss')) + '\n')
#             f.write('acc : ' + str(logs.get('binary_accuracy')) + '\n')
#             f.write('lr : ' + str(logs.get('lr')) + '\n')
#             f.write('*' * 20 + '\n')
#         with open(os.path.join(self.save_path, "epoch_val_loss_" + str(self.time_str) + ".txt"), 'a') as f:
#             f.write('epoch : ' + str(epoch + 1) + '\n')
#             f.write('val_loss : ' + str(logs.get('val_loss')) + '\n')
#             f.write('val_acc : ' + str(logs.get('val_binary_accuracy')) + '\n')
#             f.write('lr : ' + str(logs.get('lr')) + '\n')
#             f.write('*' * 20 + '\n')
#         self.loss_plot()

#     def loss_plot(self):
#         iters = range(len(self.losses))

#         plt.figure()
#         plt.plot(iters, self.losses, 'red', linewidth = 2, label='train loss')
#         plt.plot(iters, self.val_loss, 'coral', linewidth = 2, label='val loss')
#         try:
#             if len(self.losses) < 25:
#                 num = 5
#             else:
#                 num = 15
            
#             plt.plot(iters, scipy.signal.savgol_filter(self.losses, num, 3), 'green', linestyle = '--', linewidth = 2, label='smooth train loss')
#             plt.plot(iters, scipy.signal.savgol_filter(self.val_loss, num, 3), '#8B4513', linestyle = '--', linewidth = 2, label='smooth val loss')
#         except:
#             pass

#         plt.grid(True)
#         plt.xlabel('Epoch')
#         plt.ylabel('Loss')
#         plt.title('A Loss Curve')
#         plt.legend(loc="upper right")

#         plt.savefig(os.path.join(self.save_path, "epoch_loss_" + str(self.time_str) + ".png"))

#         plt.cla()
#         plt.close("all")