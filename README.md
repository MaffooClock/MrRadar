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

### Docker

The easiest way to run this utility is with Docker, which guarantees that you won't have any dependency issues.

1. First, build the image:
    ```shell
    docker build -t mr_radar:latest .
    ```

2. Then run it (minimal command to output `--help`):
    ```shell
    docker run -t --rm mr_radar:latest
    ```


### Conda

[Conda](https://docs.conda.io/en/latest/) make managing Python environments easy.

1. Start by creating the environment, which will also install the required dependencies:
    ```shell
    cd MrRadar
    conda env create -f environment.yml 
    ```

2. Activate the environment:
    ```shell
    conda activate mr_radar
    ```

3. Then run it:
    ```shell
    python3 -m run mr_radar --help
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

3. Install the dependencies
    ```shell
    python3 -m pip install -r requirements.txt
    ```

4. Then run it:
    ```shell
    python3 -m run mr_radar --help
    ```


## Usage

The instructions below show running this utility with just `mr_radar`, but the actual invocation will depend on whether you installed via Docker or Conda/Pip, so adjust accordingly.


### Positional arguments

There are two positional arguments that are required:
```shell
mr_radar <command> <site>
```


#### Command:
 1. `map`: generate the geographical map that will serve as the background to the NEXRAD imagery frames
 2. `frames`: generate one or more NEXRAD image frames
 3. `dump-products`: Dump a list of valid radar products to the console for the given site without generating any imagery

Typically, the `map` command is only ever needed once; the only time you'd want to run it again would be for a different site or radius.  The `frames` command would then be executed at some interval to have the latest quantity of frames available at all times.


#### Site:

This is the four-letter site code (known as the ICAO) of the radar site from which you want to use NEXRAD data.  Consult the [NWS Radar Operations Center](https://www.roc.noaa.gov/branches/program-branch/site-id-database.php) for various methods on finding available radar sites.


### Optional Arguments

Here are the flags with explanations of each:

<!--
    We'll need to use these to prevent the table from word-wrapping in the first two columns:
        Non-breaking hyphen: &#8209;
        Non-breaking space:  &#160; or &nbsp;
-->

| Flag                                | Default                                                                         | Description                                                                                                                                                                             |
|-------------------------------------|---------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| &#8209;&#8209;radius<br />&#8209;r  | 150                                                                             | The distance in miles around the radar site that you'd like to feature in the generated images                                                                                          |
| &#8209;&#8209;root<br />&#8209;R    | Dockerized:&nbsp;`/data`<br />Direct:&nbsp;`./out` in current working directory | The root path for all output (JSON cache file and generated images)                                                                                                                     |
| &#8209;&#8209;images<br />&#8209;i  | `./<site_id>` relative to root path                                             | The directory in which the generated PNG files will be saved, which will be relative to the root path.<br /><br />Specify an absolute path to save the images outside of the root path. |
| &#8209;&#8209;file<br />&#8209;f    | Map&nbsp;mode:&nbsp;`map.png`<br />Frames&nbsp;mode:&nbsp;`frame_<i>.png`       | The file name to use for the generated PNG file(s).<br />It is not necessary to include the `.png` extension.                                                                           |
| &#8209;&#8209;frames<br />&#8209;n  | 12                                                                              | The quantity of NEXRAD imagery frames to generate                                                                                                                                       |
| &#8209;&#8209;product<br />&#8209;p | Reflectivity                                                                    | The radar product to use for generating NEXRAD imagery frames.<br /><br />Hint: use the `dump-products` command to find the one you want.                                               |


> [!TIP]
> When running in Docker, don't forget to map the `/data` directory within the container to a local path, or you won't get any of the generated images:
> ```shell
> docker run -t --rm --volume $(pwd)/out:/data mr_radar:latest <command> <site_id>
> ```


### Example Usage

Generate a map with a 150-mile radius centered around KSJT:
```shell
mr_radar map KSJT
```
This will result in a new PNG file at `./out/ksjt/map.png`. 

Generate 12 of the latest NEXRAD frames for the same location and radius:
```shell
mr_radar frames KSJT
```
This will result in 12 new PNG files at `./out/ksjt/frame_0.png` through `./out/ksjt/frame_11.png`.


### Data Caching

You will also find a new JSON file (`./out/ksjt.json`, in this example) in the root output path, which contains the command-line arguments you supplied, as well as additional derived information based on the site ID and radius.

Here's what it's good for:
1. This makes subsequent runs faster and more efficient by re-using information rather than having to make repeated requests for information that would never change (such as radar site coordinates, for instance).
2. You will no longer need any of the optional command-line arguments on subsequent runs; those values will be read from this file if they are not present on the command line.

Deleting this file won't hurt anything, but it's not a necessary task in the course of normal use.


## Using in HTML

Check out the [`html`](./html) directory for a basic example of how to "animate" the frames on top of the base map.

The example HTML will work out-of-the-box if you run the utility with:
1. default root file path (`./out`)
2. default file names (`map.png` and `frame_<i>.png`).
3. specify `--images .` to save generated images in the root path

Otherwise, you'll need to tweak the [`loop.html`](./html/loop.html) file to make it work.

To view the animated loop after generating the map and NEXRAD frames, simply open the `loop.html` file in your browser (no web server needed to test-drive locally).

> [!IMPORTANT]
> The example HTML files aren't intended to be deployed as-is to your website, they're just an example to show how to create an animated loop effect (but you may certainly copy/paste to your heart's desire).

