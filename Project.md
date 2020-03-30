# CS4273Project

## Follow setup 

[Google Vision local set](https://cloud.google.com/vision/docs/quickstart-client-libraries)

### Basic overview


instatall google-cloude-vision by runnning `pip install --upgrade google-cloud-vision`

Install google-cloud-storage `pip install --upgrade google-cloud-storage`

set up you Authentication. At the begining of git Repo there is a file called `gVisionAuth.json`

We will need to link `gVisionAuth.json` to a environment variable

#### Mac/linux

`export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/[FILE_NAME].json"`


#### Windows

##### With PowerShell

`$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\username\Downloads\[FILE_NAME].json"`

##### CMD

`set GOOGLE_APPLICATION_CREDENTIALS=[PATH]`

[More info at](https://cloud.google.com/vision/docs/ocr#vision_text_detection-python)


### CropImages

run `pip install Pillow`
run `pip install Gooey` 
