import React from 'react';
import PropTypes from 'prop-types';

export default function Resource(props) {
  const { resource } = props;

  return (
    <div className="news-card-resource">
      <div className="resource-name flex-column">{resource.name}</div>
      <a
        className="resource-download"
        href={resource.file}
        download={resource.name}
      >
        <button className="button green-button" type="button">
          Télécharger
        </button>
      </a>
    </div>
  );
}

Resource.propTypes = {
  resource: PropTypes.shape({
    name: PropTypes.string.isRequired,
    file: PropTypes.string.isRequired,
  }).isRequired,
};
