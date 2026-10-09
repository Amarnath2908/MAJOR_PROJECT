import React, { Component } from 'react';
import { Box, RotateCcw } from 'lucide-react';
import Button from '../common/Button';

export class ViewerErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('3D Viewer Error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-full h-full min-h-[400px] flex flex-col items-center justify-center p-8 bg-dark-900 border border-slate-800 rounded-2xl text-center">
          <div className="p-4 rounded-2xl bg-red-950/40 border border-red-800/60 text-red-400 mb-4">
            <Box className="w-8 h-8" />
          </div>
          <h3 className="text-base font-semibold text-slate-200">
            Could not render 3D space model
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mt-1 mb-5">
            {this.state.error?.message ||
              'The 3D GLB file could not be parsed. You can download the model directly or return to the studio.'}
          </p>
          <div className="flex items-center gap-3">
            <Button
              size="sm"
              variant="outline"
              onClick={this.handleReset}
              leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
            >
              Retry Loading
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ViewerErrorBoundary;
