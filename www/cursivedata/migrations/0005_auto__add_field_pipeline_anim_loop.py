# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Pipeline.anim_loop'
        db.add_column('cursivedata_pipeline', 'anim_loop',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Pipeline.anim_loop'
        db.delete_column('cursivedata_pipeline', 'anim_loop')


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
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 5, 25, 0, 0)'}),
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
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 5, 25, 0, 0)'}),
            'last_used': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 5, 25, 0, 0)'}),
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
            'data_type': ('django.db.models.fields.CharField', [], {'default': "'float'", 'max_length': '20'}),
            'default': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '200', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "'Some parameter'", 'max_length': '1000', 'blank': 'True'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cursivedata.Generator']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cursivedata.pipeline': {
            'Meta': {'object_name': 'Pipeline'},
            'anim_autoplay': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'anim_loop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'anim_speed': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
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
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 5, 25, 0, 0)'}),
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