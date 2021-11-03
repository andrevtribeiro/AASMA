import tensorflow as tf

import numpy as np

import matplotlib.pyplot as plt

fname="initial_data/dataset.txt"


class NeuralNetwork:
    def __init__(self):
        try:
            self.multi_layer_model=tf.keras.models.load_model('initial_data/NN_model.h5')
    
        except:
            print("creating network and learning")
            self.createModel()
            self.learnFromDataset("initial_data/dataset.txt")
            
    def createModel(self):
        self.multi_layer_model = tf.keras.Sequential(name='multi_layer')
        self.n_classes=7
        self.inputShape=(15,)
        self.multi_layer_model.add(tf.keras.layers.Input(self.inputShape))
        self.multi_layer_model.add(tf.keras.layers.Dense(30, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.0001), name='hidden'))
        self.multi_layer_model.add(tf.keras.layers.Dense(self.n_classes, activation='softmax', name='output'))
        self.multi_layer_model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.multi_layer_model.summary()

    def learnFromDataset(self,fname):
        with open(fname, "r") as f:
                data = f.read()
        data=data.split('\n')[:-1]

        data_x=[]
        data_y=[]

        for d in data:
            aux=d[1:].split(']')
            data_x+=[[float(i) for i in aux[0].split(',')]]
            data_y+=[int(aux[1])]
        data_x = np.asarray(data_x)
        data_y = np.asarray(data_y)
        for f, c in zip(data_x[:5], data_y[:5]):
            print('Features: {}\tClass: {}'.format(f,c))

        earlystop = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=50, verbose=1)
        checkpoint = tf.keras.callbacks.ModelCheckpoint('initial_data/multi_layer_best.h5', monitor='val_accuracy', verbose=1, save_best_only=True)
        multi_layer_train = self.multi_layer_model.fit(data_x, data_y, validation_split=0.2, callbacks=[earlystop,checkpoint], epochs=10000, batch_size=32)
        self.multi_layer_model.load_weights('initial_data/multi_layer_best.h5')
        self.multi_layer_model.save('initial_data/NN_model.h5')
        
        loss, acc = self.multi_layer_model.evaluate(data_x, data_y)
        print('Accuracy: {}'.format(acc))

        fig, (loss_ax, acc_ax) = plt.subplots(1, 2, figsize=(20,7))

        loss_ax.set_title('Loss')
        loss_ax.plot(multi_layer_train.history['loss'], '-r', label='Train')
        loss_ax.plot(multi_layer_train.history['val_loss'], '-g', label='Validation')

        acc_ax.set_title('Accuracy')
        acc_ax.plot(multi_layer_train.history['accuracy'], '-r', label='Train')
        acc_ax.plot(multi_layer_train.history['val_accuracy'], '-g', label='Validation')

        plt.legend(loc=4)

        plt.savefig('initial_data/NN.png')
        plt.close()

    
    def predict(self,data):
        predictions = self.multi_layer_model.predict(data)
        return np.argmax(predictions)
