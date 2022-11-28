import React from 'react';
import { Bar } from 'react-chartjs-2';
import 'chartjs-plugin-zoom';
import { Chart, CategoryScale, LinearScale, BarElement } from 'chart.js';
Chart.register(CategoryScale, LinearScale, BarElement);

class ConsumptionsGraph extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: { count: [], index: [] },
      timeline: 'year',
      timeline_id: 0,
      timeline_name: 'année',
    };
    this.changeTimeline = this.changeTimeline.bind(this);
    this.fetch = this.fetch.bind(this);
    this.data = this.data.bind(this);
  }

  fetch(timeline) {
    fetch(Urls['student_transactions_pochtron']() + '?timeline=' + timeline)
      .then((response) => response.json())
      .then((response) => {
        this.setState({ data: response });
        return response;
      })
      .then((response) => console.log(response));
  }

  componentDidMount() {
    this.fetch(this.state.timeline);
  }

  crunchData(data) {
    var labels = [];
    var values = [];
    var datasets = [];
  }

  changeTimeline() {
    var timelines = ['year', 'month', 'day', 'hour', 'minute'];
    var timelines_names = ['année', 'mois', 'jour', 'heure', 'minute'];
    var new_id = (this.state.timeline_id + 1) % 5;
    this.setState({
      timeline: timelines[new_id],
      timeline_id: new_id,
      timeline_name: timelines_names[new_id],
    });
    this.fetch(timelines[new_id]);
  }

  data = () => ({
    labels: [
      'Janvier',
      'Février',
      'Mars',
      'Avril',
      'Mai',
      'Juin',
      'Juillet',
      'Aout',
      'Septembre',
      'Octobre',
      'Novembre',
      'Décembre',
    ],
    datasets: [
      {
        label: 'Dataset 1',
        borderColor: 'white',
        backgroundColor: 'green',
        data: this.state.data.count,
      },
    ],
  });

  scaleOpts = {
    grid: {
      borderColor: 'red',
      color: 'green',
    },
    title: {
      display: true,
      text: (ctx) => ctx.scale.axis + ' axis',
    },
  };

  scales = {
    x: {
      type: 'category',
    },
    y: {
      type: 'linear',
      ticks: {
        callback: (val, index, ticks) =>
          index === 0 || index === ticks.length - 1 ? null : val,
      },
    },
  };

  config = {
    data: this.data(),
    options: {
      scales: this.scales,
      plugins: {
        tooltip: false,
        zoom: {
          pan: {
            enabled: true,
            mode: 'x',
            modifierKey: 'ctrl',
          },
          zoom: {
            drag: {
              enabled: true,
            },
            mode: 'x',
          },
        },
      },
    },
  };

  actions = [
    {
      name: 'Reset zoom',
      handler(chart) {
        chart.resetZoom();
      },
    },
  ];

  render() {
    return (
      <div style={{ backgroundColor: 'white', width: '80%', margin: 'auto' }}>
        <div>
          <button onClick={this.changeTimeline}>
            Par {this.state.timeline_name}.
          </button>
        </div>
        <Bar data={this.config.data} options={this.config.options}></Bar>
      </div>
    );
  }
}

export { ConsumptionsGraph };
