/**
 * Migration Scripts
 */
import {createElementFromHTML} from './utils.js'

// Default options
const defaultOptions = {
    upgradeTrigger: '.migration-upgrade',
    downgradeTrigger: '.migration-downgrade',
    refreshTrigger: '.migration-refresh',
    addTrigger: '.migration-add',
    nameInputSelector: '#migration-name-input',
    errorClasses: 'red lighten-2',
    successClasses: 'green lighten-2'
}

export default class {
    /**
     * Set options and bind events.
     * @param {String} selector Migration list selector
     * @param {Object} options Configuration
     */
    constructor(selector, options={}) {
        this.el = $(selector);
        this.options = {...defaultOptions, ...options};
        this.options.statusUrl = this.el.data('status-url');

        // Bind events
        $('body')
            .on('click', this.options.upgradeTrigger, this.action.bind(this))
            .on('click', this.options.downgradeTrigger, this.action.bind(this))
            .on('click', this.options.refreshTrigger, this.action.bind(this))
            .on('click', this.options.addTrigger, this.add.bind(this));
    }

    /**
     * Event action.
     * @param {Event} e
     */
    action(e) {
        this._fetch(e.target.href);
        e.preventDefault();
    }

    /**
     * Add migration event.
     * @param {Event} e
     */
    add(e) {
        e.preventDefault();
        const data = new FormData();
        data.append('name', $(this.options.nameInputSelector).val());

        this._fetch(e.target.href, { method: 'POST', body: data })
    }

    /**
     * Updates the migration list.
     */
    update_list() {
        fetch(this.options.statusUrl)
            .then(response => response.json())
            .then(migration => {
                this.el.find(':first').replaceWith($(createElementFromHTML(migration)).find(':first'));
            });
    }

    /**
     * Fetches a resource and displays a toast with status infos and updates migration list.
     * @param {String} url URL to fetch
     * @param {Object} config fetch config
     */
    _fetch(url, config = { method: 'GET' }) {
        fetch(url, config)
            .then(response => response.json())
            .then(msg => {
                const html = msg['message'].trim().split('\n').join('<br />');
                const classes = msg['status'] == 'error' ? this.options.errorClasses : this.options.successClasses;

                M.toast({html, classes});
                this.update_list();
            });
    }
}
