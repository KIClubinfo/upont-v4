import { render } from 'react-dom';
import Vracs from '../components/EpiceriePage/VracsIndex';

// @ts-ignore window.react_mount is declared in django template
render(<Vracs />, window.react_mount);
