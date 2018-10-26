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
        $('.finished_at > time').text(new Date().toLocaleString());
    }

    /**
     * Add an item to the log
     * @param {object} item Data item object
     */
    const log = (item) => {
        $('.log').append(
            `<pre style="margin: 0;" class="green-text"><code style="font-size: 1rem; ${item.error ? 'font-weight: bold' : ''}">${item.data}</code></pre>`
        ).animate({ scrollTop: $('.log').outerHeight() });

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
        $('.started_at > time').text(new Date().toLocaleString());

        const source = new EventSource(src);
        let started = false;

        source.onmessage = function(e) {
            // Stream started
            if (!started) {
                $('.loading').remove();
                started = true;
            }

            // Stream finished
            if (e.data == 'finished') {
                return finish(source);
            }

            // Add data to log
            log(JSON.parse(e.data));
        }
    }

    // Make log stream public
    window.log_stream = log_stream;
})(jQuery);
