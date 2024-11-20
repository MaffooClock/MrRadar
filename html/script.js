
// The slight pause between every frame
const delayNextFrame =  120;

// A longer pause for the last frame, indicates the end of the loop before repeating
const delayLastFrame = 1000;

// Get the element which will contain the frame images
const framesContainer = document.querySelector('.radar-container .frames-container')

function doPreload()
{
    // Get the preload element for the map
    let map = document.querySelector('head link[rel="preload"][as="image"].preload-map');

    // Get a list of preload elements for the NEXRAD frames
    let frames = document.querySelectorAll('head link[rel="preload"][as="image"].preload-frame');

    // Convert map preloader to background image (will be a map visible through transparency of NEXRAD frames)
    framesContainer.style.backgroundImage = 'url(' + map.href + ')';
    map.remove()

    // Convert preload tags into image elements
    frames.forEach( frame => setImage( frame ) );

    // Set the first NEXRAD frame as visible (all frames are invisible by default)
    framesContainer.querySelector('img:first-of-type').classList.add('visible');
}

function setImage( preloadElement )
{
    // Pull a new image object out of thin air
    let frame = new Image();

    // Set the source of this image object to the `href=""` of the preload element
    frame.src = preloadElement.href;

    // Inject the image object as a tag inside the frames container
    framesContainer.appendChild( frame );

    // Remove the preload element from the DOM -- not necessary, but we won't need it again, so may as well tidy up
    preloadElement.remove();
}

function nextImage( activeImage )
{
    // The next image is either a sibling, or wrap around to the first one if we're at the last one
    let nextImage = ( activeImage.nextElementSibling == null ) ? activeImage.parentElement.firstElementChild : activeImage.nextElementSibling;

    // The magic sauce that causes a noticable pause when displaying the last image in the loop
    let delay = ( nextImage == activeImage.parentElement.lastElementChild ) ? delayLastFrame : delayNextFrame;

    // Make the next image visible...
    nextImage.classList.add('visible');

    // ...and hide the currently-visible image
    activeImage.classList.remove('visible');

    // Repeat!
    doLoop( delay );
}

function doLoop( time )
{
    setTimeout(() => {

        // Get the element for the currently active NEXRAD frame...
        let activeImage = framesContainer.querySelector('img[class="visible"]');

        // ...then after a quick sanity check, call the function to activate the next image
        if( activeImage )
            return nextImage( activeImage );

        // If the sanity check failed, this is where you'd take some kind of recovery action, such as updating the UI
        // to inform the user that the animation crashed.  For this example, we'll just barf a message to the console
        console.error( 'Unable to determine currently visible frame.  Animation loop terminated.' )

    }, time );
}

(function() {

    // This stuff runs when the DOM is ready

    console.info( 'Preloading images...' )
    doPreload();
    console.info( '...done.' )

    console.info( 'Starting animation loop...' )
    doLoop( delayNextFrame );
    console.info( '...looping' )

}());
