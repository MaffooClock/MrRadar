
const delayNextFrame =  120;
const delayLastFrame = 1000;

function doLoop( time )
{
    setTimeout(() => {

        let activeImage = document.querySelector('.radar-container img[class="visible"]');
        let nextImage = ( activeImage.nextElementSibling == null ) ? activeImage.parentElement.firstElementChild : activeImage.nextElementSibling;
        let delay = ( nextImage == activeImage.parentElement.lastElementChild ) ? delayLastFrame : delayNextFrame;

        nextImage.classList.add('visible');
        activeImage.classList.remove('visible');

        doLoop( delay );

    }, time );
}

(function() {

    doLoop( delayNextFrame );

}());