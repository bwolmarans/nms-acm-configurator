class Dog:                   
    def __init__(self,dogBreed,dogEyeColor):
        self.breed = dogBreed       
        self.eyeColor = dogEyeColor


tomita = Dog("Fox Terrier","brown")
print("This dog is a",tomita.breed,"and its eyes are",tomita.eyeColor)
