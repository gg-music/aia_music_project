from tensorflow.keras.optimizers import Adam
from gtzan.segmentation_models.unet import Unet as Generator
from gtzan.model.pix2pix import discriminator as Discriminator

generator_g = Generator(backbone_name='vgg16',
                        input_shape=(None, None, 3),
                        decoder_filters=(512, 512, 256, 128, 64),
                        classes=3,
                        activation='tanh')

generator_f = Generator(backbone_name='vgg16',
                        input_shape=(None, None, 3),
                        decoder_filters=(512, 512, 256, 128, 64),
                        classes=3,
                        activation='tanh')

discriminator_x = Discriminator(norm_type='instancenorm', target=False)
discriminator_y = Discriminator(norm_type='instancenorm', target=False)

generator_g_optimizer = Adam(2e-4, beta_1=0.5)
generator_f_optimizer = Adam(2e-4, beta_1=0.5)

discriminator_x_optimizer = Adam(2e-4, beta_1=0.5)
discriminator_y_optimizer = Adam(2e-4, beta_1=0.5)