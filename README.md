# NEXRAD Radar Loop Generator

<p align="center">
  <img src="https://github.com/user-attachments/assets/e45fa3ef-298b-4c7f-ba58-d82e0837f5b1" alt="Mr. Radar from Spaceballs" />
</p>

This utility will generate a base map and any number of the most recent NEXRAD radar imagery frames, with the primary
purpose of displaying an "animated" loop in HTML.

It uses [python-awips](https://github.com/Unidata/python-awips) to pull raw NEXRAD level III radar data from the
[EDEX](https://unidata.github.io/awips2/#edex) server maintained by UCAR's
[Unidata Program Center](https://www.unidata.ucar.edu/software/awips2/) in Boulder, Colorado.



## Installation

If you're using Anaconda, installation into an isolated environment is easy:
```shell
conda env create -f environment.yml 
```

...then activate the environment:
```shell
conda activate mr_radar
```

...and finally, run the following for usage information:
```shell
python3 mr_radar -h
```

Map generation is usually only needed once, and all you'll ever do after that is refresh the NEXRAD frames.

Of course, you'll need to re-generate the map if you change the site or radius (and be sure to use the same values
for the image frame generation, in case that wasn't obvious).


## Usage

The only required arguments are the mode argument (`map` or `frames`) and the 4-letter site ID for `--site` (or `-s`).

Here are the flags with explanations of each:

| Flag              | Required | Default                                                        | Description                                                                                                   |
|-------------------|:--------:|----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| --site<br />-s    |    ✓     | (none)                                                         | The 4-letter site ID                                                                                          |
| --radius<br />-r  |    ✕     | 250                                                            | The distance in miles around the radar site that<br />you'd like to cover in the generated images             |
| --path<br />-p    |    ✕     | `./out`                                                        | The path where generated PNG files will be saved                                                              |
| --file<br />-f    |    ✕     | Map mode: `<site_id>.png`<br />Frames mode: `frame_<i>.png`    | The file name to use for the generated PNG file(s).<br />It is not necessary to include the `.png` extension. |
| --frames<br />-n  |    ✕     | 12                                                             | The quantity of NEXRAD imagery frames<br />(PNG files) to generate                                            |


Generate a map with a 250-mile radius centered around KSJT:
```shell
python3 mr_radar map --site KSJT
```
This will result in a new PNG file at `./out/ksjt.png`. 

Generate 12 of the latest NEXRAD frames for the same location and radius:
```shell
python3 mr_radar frames --site KSJT
```
This will result in 12 new PNG files at `./out/frame_0.png` through `./out/frame_11.png`.


## Using in HTML

Check out the `html` directory for a basic example of how to "animate" the frames on top of the base map.

You'll have to make a few of your own tweaks to make it work out-of-the-box (hint: edit `style.css` to set the name of
the map image, and `loop.html` to set the name of the image frames).

## 
