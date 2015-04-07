# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataStore'
        db.create_table('cursivedata_datastore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cursivedata', ['DataStore'])

        # Adding model 'DataPoint'
        db.create_table('cursivedata_datapoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(default={})),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('datastore', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.DataStore'])),
            ('current', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('cursivedata', ['DataPoint'])

        # Adding model 'COSMSource'
        db.create_table('cursivedata_cosmsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Unknown Source', max_length=100)),
            ('feed_id', self.gf('django.db.models.fields.CharField')(default='96779', max_length=400)),
            ('stream_id', self.gf('django.db.models.fields.CharField')(default='1', max_length=400)),
            ('api_key', self.gf('django.db.models.fields.CharField')(default='WsH6oBOmVbflt5ytsSYHYVGQzCaSAKw0Ti92WHZzajZHWT0g', max_length=400)),
            ('cosm_trigger_id', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('cosm_url', self.gf('django.db.models.fields.CharField')(default='http://api.cosm.com/v2/triggers/', max_length=200)),
            ('add_location', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('use_stream_id', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('add_feed_title', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('add_feed_id', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_value', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
        ))
        db.send_create_signal('cursivedata', ['COSMSource'])

        # Adding M2M table for field pipelines on 'COSMSource'
        m2m_table_name = db.shorten_name('cursivedata_cosmsource_pipelines')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cosmsource', models.ForeignKey(orm['cursivedata.cosmsource'], null=False)),
            ('pipeline', models.ForeignKey(orm['cursivedata.pipeline'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cosmsource_id', 'pipeline_id'])

        # Adding model 'StoredOutput'
        db.create_table('cursivedata_storedoutput', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('endpoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Endpoint'], null=True, blank=True)),
            ('pipeline', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Pipeline'], null=True, blank=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Generator'], null=True, blank=True)),
            ('run_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('filetype', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=10)),
            ('status', self.gf('django.db.models.fields.CharField')(default='complete', max_length=10)),
            ('filename', self.gf('django.db.models.fields.CharField')(default='output/none', max_length=200)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('cursivedata', ['StoredOutput'])

        # Adding model 'Endpoint'
        db.create_table('cursivedata_endpoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('run_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 2, 25, 0, 0))),
            ('full_svg_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('last_svg_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('full_image_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('last_image_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('img_width', self.gf('django.db.models.fields.IntegerField')(default=500)),
            ('img_height', self.gf('django.db.models.fields.IntegerField')(default=500)),
            ('name', self.gf('django.db.models.fields.CharField')(default='default', max_length=200)),
            ('generate_gcode', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('device', self.gf('django.db.models.fields.CharField')(default='web', max_length=200)),
            ('width', self.gf('django.db.models.fields.FloatField')(default=200, max_length=200)),
            ('height', self.gf('django.db.models.fields.FloatField')(default=200, max_length=200)),
            ('side_margin', self.gf('django.db.models.fields.FloatField')(default=10, max_length=200)),
            ('top_margin', self.gf('django.db.models.fields.FloatField')(default=10, max_length=200)),
            ('paused', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(default='default', max_length=200)),
            ('location', self.gf('django.db.models.fields.CharField')(default='default', max_length=200)),
            ('robot_svg_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('status_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('cursivedata', ['Endpoint'])

        # Adding model 'GCodeOutput'
        db.create_table('cursivedata_gcodeoutput', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('endpoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Endpoint'])),
            ('served', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('cursivedata', ['GCodeOutput'])

        # Adding model 'Generator'
        db.create_table('cursivedata_generator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(default='Unknown', max_length=2000)),
            ('image', self.gf('django.db.models.fields.CharField')(default='No Image', max_length=200)),
            ('file_path', self.gf('django.db.models.fields.CharField')(default='./generators', max_length=200)),
            ('module_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 2, 25, 0, 0))),
            ('last_used', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 2, 25, 0, 0))),
        ))
        db.send_create_signal('cursivedata', ['Generator'])

        # Adding model 'Parameter'
        db.create_table('cursivedata_parameter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('default', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default='Some parameter', max_length=1000, blank=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Generator'])),
        ))
        db.send_create_signal('cursivedata', ['Parameter'])

        # Adding model 'GeneratorState'
        db.create_table('cursivedata_generatorstate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Generator'])),
            ('params', self.gf('jsonfield.fields.JSONField')(default={})),
            ('state', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('cursivedata', ['GeneratorState'])

        # Adding model 'Pipeline'
        db.create_table('cursivedata_pipeline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('run_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 2, 25, 0, 0))),
            ('full_svg_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('last_svg_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('full_image_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('last_image_file', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('img_width', self.gf('django.db.models.fields.IntegerField')(default=500)),
            ('img_height', self.gf('django.db.models.fields.IntegerField')(default=500)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=2000, blank=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Generator'])),
            ('data_store', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cursivedata.DataStore'], unique=True)),
            ('state', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cursivedata.GeneratorState'], unique=True)),
            ('endpoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cursivedata.Endpoint'])),
            ('paused', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('print_top_left_x', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('print_top_left_y', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('print_width', self.gf('django.db.models.fields.FloatField')(default=500)),
            ('auto_begin_days', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('next_auto_begin_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('cursivedata', ['Pipeline'])

        # Adding M2M table for field sources on 'Pipeline'
        m2m_table_name = db.shorten_name('cursivedata_pipeline_sources')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pipeline', models.ForeignKey(orm['cursivedata.pipeline'], null=False)),
            ('cosmsource', models.ForeignKey(orm['cursivedata.cosmsource'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pipeline_id', 'cosmsource_id'])


    def backwards(self, orm):
        # Deleting model 'DataStore'
        db.delete_table('cursivedata_datastore')

        # Deleting model 'DataPoint'
        db.delete_table('cursivedata_datapoint')

        # Deleting model 'COSMSource'
        db.delete_table('cursivedata_cosmsource')

        # Removing M2M table for field pipelines on 'COSMSource'
        db.delete_table(db.shorten_name('cursivedata_cosmsource_pipelines'))

        # Deleting model 'StoredOutput'
        db.delete_table('cursivedata_storedoutput')

        # Deleting model 'Endpoint'
        db.delete_table('cursivedata_endpoint')

        # Deleting model 'GCodeOutput'
        db.delete_table('cursivedata_gcodeoutput')

        # Deleting model 'Generator'
        db.delete_table('cursivedata_generator')

        # Deleting model 'Parameter'
        db.delete_table('cursivedata_parameter')

        # Deleting model 'GeneratorState'
        db.delete_table('cursivedata_generatorstate')

        # Deleting model 'Pipeline'
        db.delete_table('cursivedata_pipeline')

        # Removing M2M table for field sources on 'Pipeline'
        db.delete_table(db.shorten_name('cursivedata_pipeline_sources'))


    models = {
        'cursivedata.cosmsource': {
            'Meta': {'object_name': 'COSMSource'},
            'add_feed_id': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'add_feed_title': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'add_location': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'api_key': ('django.db.models.fields.CharField', [], {'default': "'WsH6oBOmVbflt5ytsSYHYVGQzCaSAKw0Ti92WHZzajZHWT0g'", 'max_length': '400'}),
            'cosm_trigger_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'cosm_url': ('django.db.models.fields.CharField', [], {'default': "'http://api.cosm.com/v2/triggers/'", 'max_length': '200'}),
            'feed_id': ('django.db.models.fields.CharField', [], {'default': "'96779'", 'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unknown Source'", 'max_length': '100'}),
            'pipelines': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cursivedata.Pipeline']", 'symmetrical': 'False', 'blank': 'True'}),
            'stream_id': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '400'}),
            'use_stream_id': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'cursivedata.datapoint': {
            'Meta': {'object_name': 'DataPoint'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'datastore': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.DataStore']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'cursivedata.datastore': {
            'Meta': {'object_name': 'DataStore'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cursivedata.endpoint': {
            'Meta': {'object_name': 'Endpoint'},
            'device': ('django.db.models.fields.CharField', [], {'default': "'web'", 'max_length': '200'}),
            'full_image_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'full_svg_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'generate_gcode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '200', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_height': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'img_width': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'last_image_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'last_svg_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 25, 0, 0)'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '200'}),
            'paused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'robot_svg_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'run_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'side_margin': ('django.db.models.fields.FloatField', [], {'default': '10', 'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '200'}),
            'status_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'top_margin': ('django.db.models.fields.FloatField', [], {'default': '10', 'max_length': '200'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '200', 'max_length': '200'})
        },
        'cursivedata.gcodeoutput': {
            'Meta': {'object_name': 'GCodeOutput'},
            'endpoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Endpoint']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'served': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'cursivedata.generator': {
            'Meta': {'object_name': 'Generator'},
            'description': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '2000'}),
            'file_path': ('django.db.models.fields.CharField', [], {'default': "'./generators'", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'default': "'No Image'", 'max_length': '200'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 25, 0, 0)'}),
            'last_used': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 25, 0, 0)'}),
            'module_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cursivedata.generatorstate': {
            'Meta': {'object_name': 'GeneratorState'},
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Generator']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'params': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'state': ('jsonfield.fields.JSONField', [], {'default': '{}'})
        },
        'cursivedata.parameter': {
            'Meta': {'object_name': 'Parameter'},
            'default': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "'Some parameter'", 'max_length': '1000', 'blank': 'True'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Generator']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cursivedata.pipeline': {
            'Meta': {'object_name': 'Pipeline'},
            'auto_begin_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data_store': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cursivedata.DataStore']", 'unique': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2000', 'blank': 'True'}),
            'endpoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Endpoint']"}),
            'full_image_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'full_svg_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Generator']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_height': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'img_width': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'last_image_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'last_svg_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 25, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'next_auto_begin_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'paused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'print_top_left_x': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'print_top_left_y': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'print_width': ('django.db.models.fields.FloatField', [], {'default': '500'}),
            'run_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cursivedata.COSMSource']", 'symmetrical': 'False', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cursivedata.GeneratorState']", 'unique': 'True'})
        },
        'cursivedata.storedoutput': {
            'Meta': {'object_name': 'StoredOutput'},
            'endpoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Endpoint']", 'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': "'output/none'", 'max_length': '200'}),
            'filetype': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '10'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Generator']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'pipeline': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Pipeline']", 'null': 'True', 'blank': 'True'}),
            'run_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'complete'", 'max_length': '10'})
        }
    }

    complete_apps = ['cursivedata']