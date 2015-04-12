'use strict'

var SVGAnimation = {

	/* Set behaviour via these properties */
	
	refreshSpeed : 100, // Original method = 25% CPU usage, current = 35%
    minSpeed: 100,
    maxSpeed: 1000,
    currentSpeed: 500,
	_playing : false,
	
	/* Handler methods */
	
	setup : function() {
		var frameEl = document.getElementById( 'frame' ),
			speed = document.getElementById( 'speed' ),
			//SVGDocument = document.getElementById( 'embed' ).getSVGDocument().children[0],
			SVGDocument = document.getElementById( 'embed' ).getSVGDocument().documentElement,
			elements = SVGDocument.getElementsByClassName( 'frame' );
		
			frameEl.min = parseInt( elements[0].id );
		frameEl.max = parseInt( elements[elements.length-1].id );
		frameEl.value = parseInt( frameEl.max );
		//frameEl.dataset.oldValue = '' + frameEl.max;
		speed.min = this.minSpeed;
		speed.max = this.maxSpeed;
		speed.value = this.currentSpeed;
        //this was commented out by Adnan
		SVGDocument.children[0].setAttribute( 'id', 'background' );
		this._reverseNodes( SVGDocument );

		this.setFrame( frameEl.max );
	},
	play : function() {
		var me = this,
			SVGDocument = document.getElementById( 'embed' ).getSVGDocument().documentElement,
			background = SVGDocument.getElementById( 'background' ),
			frameEl = document.getElementById( 'frame' ),
			frameCount = parseInt( frameEl.value ),
			speed = parseInt( document.getElementById( 'speed' ).value );


		this.stop();
		this._playing = true;
		this.animationCounter = setInterval( function frameTimer() {
			frameCount = frameCount + speed;
			if ( frameCount >= frameEl.max ) {
				me.stop();
				return;
			}
			frameEl.value = frameCount;
			me._moveNode( background, me._getNearestFrame( frameCount, frameEl.max ) );
			me._updateTime();
		}, this.refreshSpeed );
	},
	playFromStart : function() {
		var frameEl = document.getElementById( 'frame' );
		frameEl.value = frameEl.min;
		this.play();
	},
	stop : function() {
		clearInterval( this.animationCounter );
		this._playing = false;
	},
	setFrame : function( $frame ) {
		var SVGDocument = document.getElementById( 'embed' ).getSVGDocument().documentElement,
			background = SVGDocument.getElementById( 'background' ),
			frameEl = document.getElementById( 'frame' );

		if ( !!$frame ) {
			frameEl.value = $frame;
		}

		this.stop();
		this._moveNode( background, this._getNearestFrame( frameEl.value, frameEl.max ) );
		this._updateTime();
	},
	changeSpeed : function() {
		if ( this._playing === true ) {
			this.play();
		}
	},
	
	/* Functions of specific use for SVGAnimation */
	
	_getNearestFrame : function( $startFrame, $stopFrame ) {
		var i = $startFrame, elem = null,
			SVGDocument = document.getElementById( 'embed' ).getSVGDocument();
		for ( ; elem === null && i <= $stopFrame; i++ ) {
			elem = SVGDocument.getElementById( '' + i );
		}
		return elem;
	},
	_updateTime : function() {
		var frameText = document.getElementById( 'rangeVal' );
		frameText.value = this._getTime( frame.value );
	},	
		
	/* Generically useful functions */
	
	_getTime : function( $secs ) { // Currently inactive
		var t = new Date( 1970, 0, 1 );
		t.setSeconds( $secs );
		return ( '0' + t.getHours() ).slice( -2 ) + ':' + ( '0' + t.getMinutes() ).slice( -2 ) + ':' + ( '0' + t.getSeconds() ).slice( -2 );
	},
	_moveNode : function( $node, $relation ) {

		$node.parentNode.insertBefore( $node, $relation );
	},
	_reverseNodes : function( $node ) {
		var parentNode = $node.parentNode, nextSibling = $node.nextSibling,
			frag = $node.ownerDocument.createDocumentFragment();
		parentNode.removeChild( $node );
		while( $node.lastChild ) {
			frag.appendChild( $node.lastChild );
		}
		$node.appendChild( frag );
		parentNode.insertBefore( $node, nextSibling );

		return $node;
	}
}

