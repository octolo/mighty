{% if object.is_responsive %}
ngraph.draw().responsive([
    {
        maxWidth: {{ template.sm_max_width }}, 
        width: {{ template.sm_width }},
        height: {{ template.sm_height }},
            options: {
                titleSize: {{ template.sm_title_size }},
                textSize: {{ template.sm_text_size }},
                {% if template.responsive_options and template.responsive_options.lg %}
                {% for key,value in template.responsive_options.lg.items %}
                {% if key not in object.responsive_options.lg %}{{ key }}: {{ value|lower|safe }},{% endif %}
                {% endfor %}
                {% endif %}
                {% if object.responsive_options.lg %}
                {% for key,value in object.responsive_options.lg.items %}
                {{ key }}: {{ value|lower|safe }},
                {% endfor %}
                {% for key,value in object.bar_values.responsive_options.lg.items %}
                {{ key }}: {{ value|lower|safe }},
                {% endfor %}
                {% endif %}
            },
    },
    {
        maxWidth: {{ template.md_max_width }}, 
        width: {{ template.md_width }},
        height: {{ template.md_height }},
            options: {
                titleSize: {{ template.md_title_size }},
                textSize: {{ template.md_text_size }},
                {% if template.responsive_options and template.responsive_options.md %}
                {% for key,value in template.responsive_options.md.items %}
                {% if key not in object.responsive_options.md %}{{ key }}: {{ value|lower|safe }},{% endif %}
                {% endfor %}
                {% endif %}
                {% if object.responsive_options.md %}
                {% for key,value in object.responsive_options.md.items %}
                {{ key }}: {{ value|lower|safe }},
                {% endfor %}
                {% for key,value in object.bar_values.responsive_options.md.items %}
                {{ key }}: {{ value|lower|safe }},
                {% endfor %}
                {% endif %}
            },
    },
    {
        maxWidth: null, 
        width: {{ template.lg_width }},
        height: {{ template.lg_height }},
            options: {
                titleSize: {{ template.lg_title_size }},
                textSize: {{ template.lg_text_size }},
                {% if template.responsive_options and template.responsive_options.sm %}
                {% for key,value in template.responsive_options.sm.items %}
                {% if key not in object.responsive_options.sm %}{{ key }}: {{ value|lower|safe }},{% endif %}
                {% endfor %}
                {% endif %}
                {% if object.responsive_options.sm %}
                {% for key,value in object.responsive_options.sm.items %}
                {{ key }}: {{ value|lower|safe }},
                {% endfor %}
                {% for key,value in object.bar_values.responsive_options.sm.items %}
                {{ key }}: {{ value|lower|safe }},
                {% endfor %}
                {% endif %}
            },
    },
]);
{% else %}
ngraph.draw();
{% endif %}