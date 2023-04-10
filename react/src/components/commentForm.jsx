import React from 'react';
import PropTypes from 'prop-types';
import { getCookie } from './utils/csrf';

export default class CommentForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      mode: props.mode,
      content: '',
      post_id: props.post_id,
      club: '',
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    // eslint-disable-next-line no-undef
    fetch(Urls.publish_comment())
      .then((res) => res.json())
      .then(
        (result) => {
          this.setState({ can_publish_as: result.can_publish_as });
        },
        (error) => {
          // eslint-disable-next-line no-console
          console.error(error);
        },
      );
  }

  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
  }

  handleSubmit(event) {
    event.preventDefault();
    // eslint-disable-next-line no-undef
    const url = Urls['news:comment_post'](this.state.post_id);
    const csrfmiddlewaretoken = getCookie('csrftoken');
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfmiddlewaretoken,
      },
      body: JSON.stringify({
        content: this.state.content,
        club: this.state.club,
        post: this.state.post_id,
      }),
    };
    fetch(url, requestOptions)
      .then(
        this.setState({
          content: '',
          club: '',
        }),
      )
      // eslint-disable-next-line no-console
      .then(() => console.log('Submitted successfully'))
      // eslint-disable-next-line no-console
      .catch((error) => console.log('Form submit error', error));
    setTimeout(() => this.props.refreshPost(), 300);
  }

  render() {
    const options = [];
    if (this.state.can_publish_as) {
      for (const [key, value] of Object.entries(this.state.can_publish_as)) {
        if (value === 'Élève') {
          // This is the option to publish as student
          options.push(
            <option selected="selected" key={key} value="">
              {value}
            </option>,
          );
        } else {
          options.push(
            <option key={key} value={key}>
              {value}
            </option>,
          );
        }
      }
    }

    const field1 = (
      <div className="news-card-edit-comment">
        <textarea
          className="news-card-edit-comment-input"
          placeholder="Écris un commentaire..."
          type="text"
          name="content"
          id=""
          value={this.state.content}
          onChange={this.handleChange}
        />
        <button className="button green-button" type="submit">
          <i className="fas fa-paper-plane" />
        </button>
      </div>
    );

    if (this.state.mode === 'social' && options.length > 1) {
      // The user is member of at least one club, he/she can choose to comment as a club
      const field2 = (
        <div className="">
          <select
            className="profil-select"
            name="club"
            id="id_club"
            required
            value={this.state.club}
            onChange={this.handleChange}
          >
            {options}
          </select>
        </div>
      );

      return (
        <form
          className="news-card-edit-comment-container"
          method="post"
          onSubmit={this.handleSubmit.bind(this)}
        >
          Commenter en tant que :{field2}
          {field1}
          <input type="hidden" name="post" value={this.state.post_id} />
        </form>
      );
    }
    return (
      <form method="post" onSubmit={this.handleSubmit.bind(this)}>
        {field1}
        <input type="hidden" name="post" value={this.state.post_id} />
      </form>
    );
  }
}
CommentForm.propTypes = {
  mode: PropTypes.string.isRequired,
  post_id: PropTypes.number.isRequired,
  refreshPost: PropTypes.func.isRequired,
};
