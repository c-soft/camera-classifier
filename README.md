# Hass.io add-on for classification of images from RTSP feed of CCTV recorder

### Summary

This addon uses image recognition to tell if my garden furniture are covered or not. I use it to notify myself to cover them when the rain is coming.  


#### How does it work

The addon exposes "web API" (honestly, it's just one call) : `/covers-status`returning:
- `unknown` on error,
- `on` if the furniture is covered
- `off` if they're not covered

Then appropriate REST sensor configured in Home Assistant will get that information across.

What happens underneath when api is triggered:
1) Video stream is opened and one frame (image) is  taken.
2) Image is classified using Keras image recognition model.
3) As a result, `"on"` or `"off"` is returned

Keras model is read from the disk on the start of the addon. The URL should produce RTSP steram of 1080p quality, even though for recognition it gets rescaled to 320x170px.


### Usage 

WARNING: This is not a plug&play solution, please treat it more as inspiration. A lot of things may go wrong. You may waste lots of time getting this to work, fair warning.

Steps:
1) Prepare your data and train your model. When you have your model ready, overwrite my model (files: `model-covers.json` and `model_covers_saved.h5`)
2) Install modified addon on your hassio, most likely copy the dir containing it here: `\\hassio\addons`  (more info here: https://developers.home-assistant.io/docs/add-ons/tutorial/
3) Configure the url to take snapshot of the RTSP video. This is the only required parameter. In my case this looks like this:
`rtsp_url: 'rtsp://my-username:my-secret-password@192.168.2.15:554/cam/realmonitor?channel=4&subtype=0'`
4) Configure sensor on the Homeassistant side:

```
sensor:
  - platform: rest
    resource: http://local-camera-classifier:5000/covers-status
    name: Camera classifier
```
5) Enjoy! In my case, by using automation along the lines of:

```
- id: 'notify_if_furniture_not_covered_before_rain'
  alias: 'Notify when garden furniture outside is about to get rained on'
  trigger:
  - platform: time_pattern
    minutes: /20
    seconds: 0
  condition:
  - condition: and
    conditions:
    - condition: state
      entity_id: sensor.terrace_seat_cover_status
      state: 'off'
    - condition: template
      value_template: > 
        {{ states('sensor.dark_sky_precip_probability_0h')|int > 30 
        or states('sensor.dark_sky_precip_probability_1h')|int > 30
        or states('sensor.dark_sky_precip_probability_2h')|int > 30
        or states('sensor.dark_sky_precip_probability_3h')|int > 30}}
  action:
  - data_template:
      message: 'Garden furniture uncovered and its about to rain, now: {{ states("sensor.dark_sky_precip_intensity_0h")}}mm/h, in 1 hour: {{ states("sensor.dark_sky_precip_intensity_1h")}}mm/h, in 2h: {{ states("sensor.dark_sky_precip_intensity_2h")}}mm/h, in 3h: {{ states("sensor.dark_sky_precip_intensity_3h")}}mm/h'
      title: Rain
    service: notify.all_phones
``` 
### Training the model

I've attached code for training the model here:

I'm sure it's unnecessarily clunky and it can be done in a better way, but it got the job done for me. 

How to use it:
1) Collect more than 1000 of each class of images. I have collected around 2-3k each and it gave me good results (>99% accuracy). It's important to take snapshosts in different time of day, weather, placements and so on.
2) Put data in directory structure:
```
data_raw - contains 2 subdirs:
> cover_off - containing images with cover off
> cover_on - containing images with cover on
```

3) Run `crop_images.py`: this will do the following:
-- Copy files from "data_raw" directory structure into "data", splitting them randomly in proportion into testing data and training data
-- Crop all images, getting rid of parts of image where nothing happens.

4) Run `train-data.py` - this will train the model and save it on the disk

5) You can use `verify_dir.py` to run the model against all the files in your posetion, I've used it for debugging my model.

Again, I'm sure there are better way of doing it, but hey - live & learn :)