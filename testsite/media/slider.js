    function load()
    {
        var slider = document.getElementById("slider");
        //work out min and max
        svgdocument = embed.getSVGDocument();
        elements = svgdocument.getElementsByClassName("frame")
        slider.min = elements[0].id
        slider.max = elements[elements.length-1].id
        
        //old way was to read the file
        //slider.min = min;
        //slider.max = max;

        slider.value = max;
        var slider = document.getElementById('slider');
        slider.dataset.oldValue = "" + max;
        toggleVis("slider");
    }
    function toggleVis(sliderID)
    {
        var sliderText = document.getElementById("rangeVal");
        var slider = document.getElementById("slider");
        var embed = document.getElementById('embed');
        svgdocument = embed.getSVGDocument();
        var newValue = slider.value;
        var oldValue = slider.dataset.oldValue;
        slider.dataset.oldValue = newValue;
        sliderText.value = slider.value;
        if (oldValue == newValue)
            return
        else if (oldValue > newValue) {
            var displayStyle = "none";
            var startValue = +newValue;
            var stopValue = +oldValue;
        }
        else if (newValue > oldValue) {
            var displayStyle = "inline";
            var startValue = +oldValue;
            var stopValue = +newValue;
        }
        var elem;
        for (var i = startValue; !elem && i < stopValue; i++) {
            var elem = svgdocument.getElementById("" + i);
        }
        if (!elem) return;
        for (; elem.previousElementSibling && elem.previousElementSibling.id == elem.id; elem = elem.previousElementSibling);
        for (; elem && elem.id < stopValue; elem = elem.nextElementSibling) {
            elem.style.display = displayStyle;
        }
    }
