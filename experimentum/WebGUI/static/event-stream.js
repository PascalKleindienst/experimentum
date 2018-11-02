/**
 * Add Server-sent events to display experiment log
 * !Note: Not supported in MS Edge as of right now!
 */
(function($) {
    /**
     * Close the event stream and add finish experiment run
     * @param {EventSource} stream Event stream to close
     */
    const finish = (stream) => {
        stream.close()
        $('.progress').remove();
    }

    function updateScroll(){
        var element = $("#log .log").get(0);
        element.scrollTop = element.scrollHeight;
    }

    /**
     * Add an item to the log
     * @param {object} item Data item object
     */
    const log = (item) => {
        $('.log').append(
            `<pre style="margin: 0;" class="green-text"><code style="font-size: 1rem; ${item.error ? 'font-weight: bold' : ''}">${item.data}</code></pre>`
        );

        updateScroll();

        // Error indicators
        if (item.error) {
            $('.status i').text('error').addClass('red-text').removeClass('green-text');
            $('.log > pre:last').removeClass('green-text').addClass('red-text');
            $('.status-log > li.success').removeClass('success').addClass('error');
        }
    }

    /**
     * Stream the experiment log
     * @param {string} src Source url for the event stream
     */
    const log_stream = (src) => {
        const source = new EventSource(src);

        source.onmessage = function(e) {
            const data = JSON.parse(e.data);

            // Stream started
            if (data.type == 'started') {
                $('.loading').remove();
            }
            // Add data to log
            else if (data.type == 'log') {
                log(data);
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

                $('.started_at').html(start.toLocaleString());
                $('.finished_at').html(finished.toLocaleString());
                $('.config_file').html(data.data.config_file);
                $('.config_content').html(data.data.config_content);

                return finish(source);
            }
        }
    }

    // Make log stream public
    window.log_stream = log_stream;
})(jQuery);
