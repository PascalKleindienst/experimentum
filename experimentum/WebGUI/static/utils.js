/**
 * Some Utility helpers.
 */

/**
 * Create an element based on an html string
 * @param {String} htmlString HTML String
 */
export const createElementFromHTML = (htmlString) => {
    const div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}
