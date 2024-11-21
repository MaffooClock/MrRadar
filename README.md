# NEXRAD Radar Loop Generator

<p align="center">
  <img src="https://github.com/user-attachments/assets/e45fa3ef-298b-4c7f-ba58-d82e0837f5b1" alt="Mr. Radar from Spaceballs" />
</p>

This utility will generate a base map and any number of the most recent NEXRAD radar imagery frames, with the primary purpose of presenting an animated loop in HTML (but you could use the map and frames however you like).

It uses [python-awips](https://github.com/Unidata/python-awips) to pull raw NEXRAD level III radar data from the [EDEX](https://unidata.github.io/awips2/#edex) server maintained by UCAR's [Unidata Program Center](https://www.unidata.ucar.edu/software/awips2/) in Boulder, Colorado.


## Installation

The instructions below assume Linux or macOS.  The same should work in Windows, but the commands will be slightly different.


First, grab a copy of the utility:
```shell
git clone https://github.com/MaffooClock/MrRadar.git
```

### Conda

[Conda](https://docs.conda.io/en/latest/) make managing Python environments easy.

1. Start by creating the environment, which will also install the required dependencies:
    ```shell
    cd MrRadar
    conda env create -f environment.yml 
    ```

2. Then activate the environment:
    ```shell
    conda activate mr_radar
    ```

### Pip

And for those who prefer using good ol' Pip... of course, doing this in a Python [venv](https://docs.python.org/3/library/venv.html) (virtual environment) is recommended:

1. Create the venv:
    ```shell
    cd MrRadar
    python -m venv .venv
    ```

2. Activate the venv:
    ```shell
    source .venv/bin/activate
    ```

3. Then install the dependencies
    ```shell
    python3 -m pip install -r requirements.txt
    ```


## Usage

### Positional arguments

There are two positional arguments that are required:
```shell
python3 mr_radar <command> <site>
```


#### Command:
 1. `map`: generate the geographical map that will serve as the background to the NEXRAD imagery frames
 2. `frames`: generate one or more NEXRAD image frames
 3. `dump-products`: Dump a list of valid radar products to the console for the given site without generating any imagery

Typically, the `map` command is only ever needed once; the only time you'd want to run it again would be for a different site or radius.  The `frames` command would then be executed at some interval to have the latest quantity of frames available at all times.


#### Site:

This is the four-letter site code (known as the ICAO) of the WSR-88D radar site of which you want to use NEXRAD data.  Consult the [NWS Radar Operations Center](https://www.roc.noaa.gov/branches/program-branch/site-id-database.php) for various methods on finding available radar sites.


### Optional Arguments

Here are the flags with explanations of each:

| Flag              | Default                                               | Description                                                                                                                                         |
|-------------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| --radius<br />-r  | 150                                                   | The distance in miles around the radar site that<br />you'd like to cover in the generated images                                                   |
| --path<br />-P    | `./out`                                               | The path where generated PNG files will be saved                                                                                                    |
| --file<br />-f    | Map mode: `map.png`<br />Frames mode: `frame_<i>.png` | The file name to use for the generated PNG file(s).<br />It is not necessary to include the `.png` extension.                                       |
| --frames<br />-n  | 12                                                    | The quantity of NEXRAD imagery frames<br />(PNG files) to generate                                                                                  |
| --product<br />-p | Reflectivity                                          | The radar product to use for generating NEXRAD<br />imagery frames.<br /><br />Hint: use the `dump-products` command to find<br />the one you want. |


### Example Usage

Generate a map with a 150-mile radius centered around KSJT:
```shell
python3 mr_radar map KSJT
```
This will result in a new PNG file at `./out/map.png`. 

Generate 12 of the latest NEXRAD frames for the same location and radius:
```shell
python3 mr_radar frames KSJT
```
This will result in 12 new PNG files at `./out/frame_0.png` through `./out/frame_11.png`.


### Data Caching

You will also find a new JSON file (`ksjt.json`, in this example) in your current working directory, which contains the command-line arguments you supplied, as well as additional derived information based on the site ID and radius.

Here's what it's good for:
1. This information makes subsequent runs faster and more efficient by re-using that information rather than having to make repeated requests for information that would never change (such as radar site coordinates, for instance).
2. You will no longer need any of the optional command-line arguments on subsequent runs; those values will be read from this file if they are not present on the command line.  Simply run `python3 mr_radar frames <site_id>` to re-use the radius and frame count that you specified initially.

Deleting this file won't hurt anything, but it's not necessary to do so with normal use.


## Using in HTML

Check out the [`html`](/../../tree/dev/html) directory for a basic example of how to "animate" the frames on top of the base map.  It will work out-of-the-box if you run the utility with the default output file path (`./out`) and names (`map.png` and `frame_<i>.png`).

If you generate your map file and NEXRAD frames with non-default path and file names, you'll need to tweak the [`loop.html`](/../../tree/dev/html/loop.html) file to make it work.

Simply open `loop.html` in your browser (you can test drive it locally without using a web server).

> [!IMPORTANT]
> The example HTML files aren't intended to be deployed as-is to your website, they're just an example to show how to create an animated loop effect (but you may certainly copy/paste to your heart's desire).

