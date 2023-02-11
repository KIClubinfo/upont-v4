import ReactDOM from 'react-dom';
import React from 'react';
import Posts from '../components/posts';

ReactDOM.render(
  // courseId if define in django template
  // eslint-disable-next-line no-undef
  <Posts mode="course" courseId={courseId} />,
  window.react_mount,
);
