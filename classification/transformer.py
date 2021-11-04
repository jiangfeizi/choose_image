from imgaug import augmenters as iaa


class Transformer:
    def __init__(self, scale=None, translate_percent_x=None, translate_percent_y=None, rotate=None, shear=None,
                    flip_lr=None, flip_ud=None, crop=None, multiply=None, 
                    gaussian_noise=None, gaussian_blur=None, linear_contrast=None, **kwargs):
        self.seq = iaa.Sequential(random_order=True)
        if scale or translate_percent_x or translate_percent_y or rotate or shear:
            translate_percent = None
            if translate_percent_x or translate_percent_y:
                translate_percent = {}
                if translate_percent_x:
                    translate_percent.update({'x': tuple(translate_percent_x)})
                if translate_percent_y:
                    translate_percent.update({'y': tuple(translate_percent_y)})
            self.seq.add(iaa.Affine(
                            scale=tuple(scale) if scale else None,
                            translate_percent=translate_percent if translate_percent else None,
                            rotate=tuple(rotate) if rotate else None,
                            shear=tuple(shear) if shear else None,
                            order=[0, 1]
                        ))
        if flip_lr:
            self.seq.add(iaa.Fliplr(flip_lr))
        if flip_ud:
            self.seq.add(iaa.Flipud(flip_ud))
        if crop:
            self.seq.add(iaa.Crop(percent=tuple(crop)))
        if multiply:
            self.seq.add(iaa.Multiply(tuple(multiply)))
        if gaussian_noise:
            self.seq.add(iaa.Sometimes(0.5, iaa.AdditiveGaussianNoise(loc=0, scale=tuple(gaussian_noise), per_channel=0.5)))
        if gaussian_blur:
            self.seq.add(iaa.Sometimes(0.5, iaa.GaussianBlur(tuple(gaussian_blur))))
        if linear_contrast:
            self.seq.add(iaa.LinearContrast(tuple(linear_contrast)))

    def __call__(self, image):
        aug_image = self.seq.augment_image(image)
        return aug_image
