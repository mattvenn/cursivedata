"""Various display related classes.

"""

from IPython.core.display import DisplayObject, Javascript


class SVGSliderJS(Javascript):

    def __init__(self, feedId, width='100%', height='700px'):
        data = """
            var slider = $('<input type="range" style="width:%(width)s" step="1">').appendTo(element);
            var rangeVal = $('<input type="text" size="8" />').appendTo(element);
            var embed = $('<embed src="files/tmp/%(feedId)d/concat.svg" type="image/svg+xml" style="height:%(height)s;width:%(width)s" />').appendTo(element);
            var embedElem = embed[0];

            var toggleVis = function () {
                var svgdocument = embedElem.getSVGDocument();
                var newValue = slider.val();
                var oldValue = slider.data('oldValue');
                slider.data('oldValue', newValue);
                rangeVal.val(slider.val());
                if (oldValue == newValue) {
                    return
                }
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
                for (; elem.previousElementSibling &&
                       elem.previousElementSibling.id == elem.id
                     ; elem = elem.previousElementSibling);
                for (; elem && elem.id < stopValue
                     ; elem = elem.nextElementSibling) {
                    elem.style.display = displayStyle;
                }
            };

            embedElem.onload = function() {
                var svg = $(embedElem.getSVGDocument());
                var elems = svg.find('svg').children();
                var min = +elems.first().attr('id');
                var max = +elems.last().attr('id') + 1;
                slider.change(toggleVis);
                slider.attr('min', min);
                slider.attr('max', max);
                slider.val(max);
                rangeVal.val(max);
                slider.data('oldValue', "" + max);
                toggleVis();
            };

            container.show();
        """ % {'feedId': feedId, 'width': width, 'height': height}
        super(SVGSliderJS, self).__init__(data=data)
