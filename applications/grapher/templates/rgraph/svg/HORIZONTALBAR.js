var values = {{ object.horizontalbar_values|safe }};
var labels = [];
var datas = [];
for (var key in values) {
    if (key !== 'options') {
        labels.push(key);
        datas.push(values[key]);
    }
}

var data = [[542,623],[453,646],[756,688]];
    
ngraph = new RGraph.SVG.HBar({
    id: 'chart-{{ template.uid }}',
    data: datas,
    options: {
        yaxisLabels: labels,
        {% if 'title' in object.options %}title: {{ object.options.title|lower|safe }},{% else %}title: '{{ object.title }}',{% endif %}
        {% include "rgraph/svg/options.js" %}
    }
});

{% include "rgraph/svg/responsive.js" %}