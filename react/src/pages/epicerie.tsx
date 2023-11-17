import { render } from 'react-dom';
import { Epicerie } from '../components/EpiceriePage/EpicerieComponents';

// @ts-ignore window.react_mount is declared in django template
render(<Epicerie />, window.react_mount);
