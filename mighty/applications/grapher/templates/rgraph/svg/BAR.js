var values = {{ object.bar_values|safe }};
var labels = [];
var datas = [];
for (var key in values) {
    if (key !== 'options') {
        labels.push(key);
        datas.push(values[key]);
    }
}

ngraph = new RGraph.SVG.Bar({
    id: 'chart-{{ template.uid }}',
    data: [datas],
    options: {
        xaxisLabels: labels,
        {% if 'title' in object.options %}title: {{ object.options.title|lower|safe }},{% else %}title: '{{ object.title }}',{% endif %}
        {% include "rgraph/svg/options.js" %}
    },
});

{% include "rgraph/svg/responsive.js" %}