odoo.define('stock_pivot.pivot', function (require){
"use strict";
var config = require('web.config');
var PivotView = require('web.PivotView');
var core = require('web.core');
var crash_manager = require('web.crash_manager');
var data_manager = require('web.data_manager');
var formats = require('web.formats');
var framework = require('web.framework');
var Model = require('web.DataModel');
var session = require('web.session');
var Sidebar = require('web.Sidebar');
var utils = require('web.utils');
var View = require('web.View');

PivotView.include({

// START

    draw_headers: function ($thead, headers) {
        var self = this,
            i, j, cell, $row, $cell,$cell1;

        var groupby_labels = _.map(this.main_col.groupbys, function (gb) {
            return self.fields[gb.split(':')[0]].string;
        });

        for (i = 0; i < headers.length; i++) {
            $row = $('<tr>');
            if(i ==1 &&  this.model=='total.stock.report.forecast'){
                $row.append('<th rowspan="1" colspan="1" title="" class="" data-original-title="Date" aria-describedby="tooltip471321"></th>');
            }
            for (j = 0; j < headers[i].length; j++) {
                cell = headers[i][j];
                if(this.model=='total.stock.report.forecast' && i== 0 && j ==1){
                    var colspan = 14;
                }else{
                    var colspan = cell.width;
                }
                $cell = $('<th>')
                .text(cell.title)
                .attr('rowspan', cell.height)
                .attr('colspan', colspan);
                if (i > 0) {
                    $cell.attr('title', groupby_labels[i-1]);
                }
                if (cell.expanded !== undefined) {
                    $cell.addClass(cell.expanded ? 'o_pivot_header_cell_opened' : 'o_pivot_header_cell_closed');
                    $cell.data('id', cell.id);
                }
                if (cell.measure) {
                      if (this.model=='total.stock.report.forecast'){
                          if(i== 2 && j ==0){
                                     var txt = "QOH";
                                }else{

                                    var txt = "Stock Forecast";
                                 }
                      }else{
                        var txt = this.measures[cell.measure].string;
                      }
                    $cell.addClass('o_pivot_measure_row text-muted')
                        .text(txt);
                    $cell.data('id', cell.id).data('measure', cell.measure);
                    if (cell.id === this.sorted_column.id && cell.measure === this.sorted_column.measure) {
                        $cell.addClass('o_pivot_measure_row_sorted_' + this.sorted_column.order);
                    }
                }
                $row.append($cell);
                $cell.toggleClass('hidden-xs', (cell.expanded !== undefined) || (cell.measure !== undefined && j < headers[i].length - this.active_measures.length));
                if (cell.height > 1) {
                    $cell.css('padding', 0);
                }
            }

//            if  (this.model=='total.stock.report.forecast' && i==1 ){
//                     var values = [];
//                     jQuery.each($row, function(i, item) {
//                            console.log("++$row+++",$row);
//                            values = values + 'td' + (i + 1) + ':' + item.innerHTML + '<br/>';
//                            console.log("+++++",i,"item..",item);
//                        });
//                     console.log("++After",$row);
//                 }

//           if  (this.model=='total.stock.report.forecast' && i==1 ){
//                     console.log("before.++.",$row[0]);
//
//
//                      jQuery.each($row[0], function(i, item) {
//                            console.log("++$row+++",$row);
//                            values = values + 'td' + (i + 1) + ':' + item.innerHTML + '<br/>';
//                            console.log("+++++",i,"item..",item);
//                        });
//
//
//
//                     var  $cell1 = '';
//                     $cell1 = $('<th>')
//                        .text('')
//                        .attr('rowspan', 1)
//                        .attr('colspan',1 );
//                      $row.prepend($cell1);
//                 }


        $thead.append($row);
        }
    },

     draw_rows: function ($tbody, rows) {
        var self = this,
            i, j, value, $row, $cell, $header,
            nbr_measures = this.active_measures.length,
            length = rows[0].values.length,
            display_total = this.main_col.width > 1;

        var groupby_labels = _.map(this.main_row.groupbys, function (gb) {
            return self.fields[gb.split(':')[0]].string;
        });
        var measure_types = this.active_measures.map(function (name) {
            return self.measures[name].type;
        });
        var widgets = this.widgets;
        for (i = 0; i < rows.length; i++) {
            $row = $('<tr>');
            $header = $('<td>')
                .text(rows[i].title)
                .data('id', rows[i].id)
                .css('padding-left', (5 + rows[i].indent * 30) + 'px')
                .addClass(rows[i].expanded ? 'o_pivot_header_cell_opened' : 'o_pivot_header_cell_closed');

            if (rows[i].indent > 0) $header.attr('title', groupby_labels[rows[i].indent - 1]);
            $header.appendTo($row);
            if  (this.model=='total.stock.report.forecast'){
                rows[i].values.unshift(rows[i].values[rows[i].values.length-1]);
                        }
            for (j = 0; j < length; j++) {
                value = formats.format_value(rows[i].values[j], {type: measure_types[j % nbr_measures], widget: widgets[j % nbr_measures]});
                if (value==0 && i==0 && this.model=='total.stock.report.forecast'){
                    var value = '';
                  }
                $cell = $('<td>')
                            .data('id', rows[i].id)
                            .data('col_id', rows[i].col_ids[Math.floor(j / nbr_measures)])
                            .toggleClass('o_empty', !value)
                            .text(value)
                            .addClass('o_pivot_cell_value text-right');
                if (((j >= length - this.active_measures.length) && display_total) || i === 0){
                    $cell.css('font-weight', 'bold');
                }
                $row.append($cell);

                $cell.toggleClass('hidden-xs', j < length - this.active_measures.length);
            }
            $tbody.append($row);
        }
    },

//    END


});
});
