/**
 * Add Server-sent events to display experiment log
 * !Note: Not supported in MS Edge as of right now!
 */
(function($) {
    /**
     * Scroll log to bottom
     * @param {string} selector Log selector
     */
    const update_scroll = (selector) => {
        const element = $(`#log ${selector} .log`).get(0);
        element.scrollTop = element.scrollHeight;
    }

    /**
     * Add an item to the log
     * @param {object} item Data item object
     */
    const log = (item, selector) => {
        $(`${selector} .log`).append(
            `<pre style="margin: 0;" class="green-text"><code style="font-size: 1rem; ${item.error ? 'font-weight: bold' : ''}">${item.data}</code></pre>`
        );

        update_scroll(selector);

        // Error indicators
        console.log(item.error, selector);
        if (item.error) {
            $(`${selector} .status i`).text('error').addClass('red-text').removeClass('green-text').removeClass('amber-text');
            $(`${selector} .log > pre:last`).removeClass('green-text').removeClass('amber-text').addClass('red-text');
            $(`.status-log ${selector}.waiting`).removeClass('waiting').addClass('error');
        }
    }

    /**
     * Stream the experiment log
     * @param {string} src Source url for the event stream
     */
    const log_stream = (src, plot_url) => {
        const source = new EventSource(src);

        source.onmessage = async function(e) {
            const data = JSON.parse(e.data);

            // Stream started
            if (data.type == 'started') {
                $('.experiment-log .loading').remove();
            }
            // Add data to log
            else if (data.type == 'log') {
                log(data, '.experiment-log');
            }
            // Result table
            else if (data.type == 'table') {
                $('#result').html(data.table);
                $('#result > table').addClass('striped').addClass('responsive-table');
            }
            // Stream finished
            else if (data.type == 'finished') {
                const start = new Date(data.data.start);
                const finished = new Date(data.data.finished);

                $('.experiment-log.waiting').removeClass('waiting').addClass('success');
                $('.experiment-log.success .material-icons').text('check_circle').removeClass('amber-text').addClass('green-text');
                $('.started_at').html(start.toLocaleString());
                $('.finished_at').html(finished.toLocaleString());
                $('.config_file').html(data.data.config_file);
                $('.config_content').html(data.data.config_content);

                await generate_plots(plot_url);
                return source.close();
            }
        }
    }

    /**
     * Generate plots and add them to the plot tab
     * @param {str} url URL to endpoint for generating plots
     */
    const generate_plots = async (url) => {
        $('.collapsible').collapsible('open', 1);

        fetch(url, { method: 'GET' })
            .then(response => response.json())
            .then(messages => {
                $('.plot-log .loading').remove();

                messages.forEach(data => {
                    // Log plot message
                    log({
                        data: data.message,
                        error: !!(data.status == 'error')
                    }, '.plot-log');

                    // add to plot tab
                    $('#plots .row').append(
                        `<div class="col s12 m6">
                            <img class="materialboxed responsive-img" src="${data.file}" />
                        </div>`
                    );
                });

                if (messages.length == 0) {
                    log({data: 'No Plots available', error: false}, '.plot-log');
                    $('#plots .row').append('<div class="col s12"><h3>No Plots available</h3></div>');
                }

                // Init lightbox and remove progressbar
                $('.plot-log.waiting').removeClass('waiting').addClass('success');
                $('.plot-log.success .material-icons').text('check_circle').removeClass('amber-text').addClass('green-text');
                $('.materialboxed').materialbox();
                $('.progress').remove()
            })
            .catch(error => {
                console.log(error)
            });
    }

    // Make log stream public
    window.log_stream = log_stream;
})(jQuery);
